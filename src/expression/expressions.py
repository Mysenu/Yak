from typing import Optional, Union
from math import sqrt, pow

from src.expression.is_valid_expression import findOperand, findOperands, ScanDirection, isExpression, VALID_CHARS


def prepareExpression(expression: str, change_math_char=False) -> str:
    converted_expression = convertToPyExpr(expression)
    return converted_expression


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def convertToPyExpr(raw_expr: str) -> str:
    for index, char in enumerate(raw_expr):
        if char == '√':
            func = 'sqrt'
            sub_expr = findOperand(raw_expr, index)
            start, end = sub_expr.start - 1, sub_expr.end
        elif char == '^':
            func = 'pow'
            sub_expr = findOperands(raw_expr, index)
            start, end = sub_expr.start, sub_expr.end
        elif char == '%':
            func = 'toPercent'
            sub_expr = findOperand(raw_expr, index, ScanDirection.Left)
            start, end = sub_expr.start, sub_expr.end + 1
        else:
            continue

        expr = f'{raw_expr[:start]}{func}({sub_expr}){raw_expr[end:]}'
        return convertToPyExpr(expr)
    else:
        return raw_expr


def calculate(expression: str) -> Optional[Union[int, float, bool]]:
    if not isExpression(expression):
        return False

    if expression.strip():
        expression = prepareExpression(expression, True)
        return eval(expression)


def canBeAdded(char: str, expression: str, position: int) -> bool:
    return char in VALID_CHARS


if __name__ == '__main__':
    def testExpr(text):
        print(f'Source: {text} | Py: {convertToPyExpr(text)}')
