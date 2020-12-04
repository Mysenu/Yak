def toEditableExpr(expression: str) -> str:
    expression = expression.replace('√', 'V')
    return expression


def fromEditableExpr(expression: str) -> str:
    expression = expression.replace('v', '√')
    return expression
