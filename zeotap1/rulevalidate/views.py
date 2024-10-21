# rules/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Rule, Node
from .serializers import RuleSerializer
from .rulesparser import create_rule_ast, evaluate_rule, combine_rules
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import os

def home(request):
    file_path = os.path.join(settings.BASE_DIR, 'templates', 'index.html')
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/html')


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    @action(detail=False, methods=['POST'])
    def create_rule(self, request):
        rule_string = request.data.get('rule_string')
        name = request.data.get('name')
        description = request.data.get('description', '')

        if not rule_string:
            return Response(
                {'error': 'rule_string is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            root_node = create_rule_ast(rule_string)
            rule = Rule.objects.create(
                name=name,
                description=description,
                root_node=root_node
            )
            return Response(RuleSerializer(rule).data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def evaluate_rule(self, request):
        rule_id = request.data.get('rule_id')
        data = request.data.get('data', {})

        if not rule_id:
            return Response(
                {'error': 'rule_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not data:
            return Response(
                {'error': 'data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rule = Rule.objects.get(id=rule_id)
            # Type validation for input data
            for key, value in data.items():
                if isinstance(value, bool):
                    continue
                if not isinstance(value, (str, int, float)):
                    return Response(
                        {'error': f'Invalid type for field {key}. Must be string, integer, or float'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            result = evaluate_rule(rule.root_node, data)
            return Response({'result': result})
        except Rule.DoesNotExist:
            return Response(
                {'error': 'Rule not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def combine_rules(self, request):
        rule_ids = request.data.get('rule_ids', [])
        name = request.data.get('name')
        description = request.data.get('description', '')

        if not rule_ids:
            return Response(
                {'error': 'rule_ids is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rules = Rule.objects.filter(id__in=rule_ids)
            if len(rules) != len(rule_ids):
                return Response(
                    {'error': 'One or more rules not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            root_nodes = [rule.root_node for rule in rules]
            combined_node = combine_rules(root_nodes)
            
            new_rule = Rule.objects.create(
                name=name,
                description=description,
                root_node=combined_node
            )
            
            return Response(RuleSerializer(new_rule).data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )