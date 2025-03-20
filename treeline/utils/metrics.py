import ast

def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """
    Calculate cyclomatic complexity for an AST node.
    
    Cyclomatic complexity counts the number of linearly independent paths through code.
    Higher complexity indicates code that may be difficult to understand and test.
    
    Args:
        node: An AST node (typically a function or class definition)
        
    Returns:
        int: The cyclomatic complexity score
    """
    try:
        complexity = 1 
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    except Exception as e:
        return 0

def calculate_cognitive_complexity(node: ast.AST) -> int:
    """    
    Cognitive complexity measures how difficult code is to understand.
    
    Returns:
        int: The cognitive complexity score
    """
    def walk_cognitive(node: ast.AST, nesting: int = 0) -> int:
        complexity = 0
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + nesting
                complexity += walk_cognitive(child, nesting + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            else:
                complexity += walk_cognitive(child, nesting)
        return complexity
    return walk_cognitive(node)

