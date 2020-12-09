def toEditableExpr(expression: str) -> str:
    expression = expression.replace('√', 'V')
    expression = expression.replace('×', '*')
    return expression


def fromEditableExpr(expression: str) -> str:
    expression = expression.replace('v', '√')
    expression = expression.replace('*', '×')
    return expression
