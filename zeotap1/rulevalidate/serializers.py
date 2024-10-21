from rest_framework import serializers
from .models import Node, Rule

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'type', 'operator', 'field_name', 'value', 'left', 'right']

class RuleSerializer(serializers.ModelSerializer):
    ast = serializers.SerializerMethodField()

    class Meta:
        model = Rule
        fields = ['id', 'name', 'description', 'root_node', 'ast', 'created_at', 'updated_at']

    def get_ast(self, obj):
        return obj.root_node.to_dict()