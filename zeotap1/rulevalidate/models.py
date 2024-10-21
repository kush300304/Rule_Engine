from django.db import models

# Create your models here.
import json

class Node(models.Model):
    NODE_TYPES = (
        ('operator', 'Operator'),
        ('operand', 'Operand'),
    )
    
    OPERATOR_CHOICES = (
        ('AND', 'AND'),
        ('OR', 'OR'),
        ('>', 'Greater Than'),
        ('<', 'Less Than'),
        ('=', 'Equals'),
        ('>=', 'Greater Than or Equal'),
        ('<=', 'Less Than or Equal'),
    )

    type = models.CharField(max_length=10, choices=NODE_TYPES)
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES, null=True, blank=True)
    field_name = models.CharField(max_length=100, null=True, blank=True)  # For operands
    value = models.JSONField(null=True, blank=True)  # Stores the comparison value
    left = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='left_child')
    right = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='right_child')

    def to_dict(self):
        result = {
            'type': self.type,
            'operator': self.operator,
            'field_name': self.field_name,
            'value': self.value,
        }
        if self.left:
            result['left'] = self.left.to_dict()
        if self.right:
            result['right'] = self.right.to_dict()
        return result
    
class Rule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    root_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='rule')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

