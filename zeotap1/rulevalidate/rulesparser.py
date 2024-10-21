# rules/rule_parser.py
import re
from .models import Node

def tokenize_rule(rule_string):
    # Split the rule string into tokens
    tokens = re.findall(r'[\w\.]+|[><=]+|\(|\)|AND|OR|\d+|\'[^\']*\'|\"[^\"]*\"', rule_string)
    return [token.strip("'\"") for token in tokens]

def get_value_with_type(value):
    """Convert string value to appropriate Python type"""
    try:
        # Try to convert to integer
        return int(value)
    except ValueError:
        try:
            # Try to convert to float
            return float(value)
        except ValueError:
            # If not numeric, return as string
            return value

def parse_condition(tokens, pos):
    field = tokens[pos]
    operator = tokens[pos + 1]
    raw_value = tokens[pos + 2]
    
    # Convert value to appropriate type
    typed_value = get_value_with_type(raw_value)
    
    # Create operand node
    node = Node.objects.create(
        type='operand',
        operator=operator,
        field_name=field,
        value=typed_value  # Store the typed value
    )
    
    return node, pos + 3

def parse_expression(tokens, pos=0):
    if tokens[pos] == '(':
        pos += 1
        left_node, pos = parse_expression(tokens, pos)
        
        if pos >= len(tokens):
            return left_node, pos
            
        if tokens[pos] in ('AND', 'OR'):
            operator = tokens[pos]
            pos += 1
            right_node, pos = parse_expression(tokens, pos)
            
            node = Node.objects.create(
                type='operator',
                operator=operator,
                left=left_node,
                right=right_node
            )
            
            if pos < len(tokens) and tokens[pos] == ')':
                pos += 1
            return node, pos
            
        if tokens[pos] == ')':
            pos += 1
            return left_node, pos
    else:
        return parse_condition(tokens, pos)

def create_rule_ast(rule_string):
    tokens = tokenize_rule(rule_string)
    root_node, _ = parse_expression(tokens)
    return root_node

def evaluate_rule(node, data):
    if node.type == 'operand':
        field_value = data.get(node.field_name)
        if field_value is None:
            raise ValueError(f"Field {node.field_name} not found in data")

        # Convert field_value to the same type as node.value
        if isinstance(node.value, (int, float)) and isinstance(field_value, (int, float)):
            # Both are numeric, proceed with comparison
            field_value = type(node.value)(field_value)
        elif isinstance(node.value, str) and isinstance(field_value, str):
            # Both are strings, proceed with comparison
            pass
        else:
            # Type mismatch
            raise ValueError(f"Type mismatch: Cannot compare {type(field_value)} with {type(node.value)}")

        if node.operator == '>':
            return field_value > node.value
        elif node.operator == '<':
            return field_value < node.value
        elif node.operator == '=':
            return field_value == node.value
        elif node.operator == '>=':
            return field_value >= node.value
        elif node.operator == '<=':
            return field_value <= node.value
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

    elif node.type == 'operator':
        left_result = evaluate_rule(node.left, data)
        right_result = evaluate_rule(node.right, data)

        if node.operator == 'AND':
            return left_result and right_result
        elif node.operator == 'OR':
            return left_result or right_result
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

def combine_rules(nodes, operator='AND'):
    if not nodes:
        raise ValueError("No rules to combine")
    if len(nodes) == 1:
        return nodes[0]

    # Create a new operator node combining the rules
    combined_node = Node.objects.create(
        type='operator',
        operator=operator,
        left=nodes[0],
        right=combine_rules(nodes[1:], operator)
    )
    
    return combined_node