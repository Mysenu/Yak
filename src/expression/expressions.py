from typing import Optional, Union
from math import sqrt, pow

from src.expression.is_valid_expression import findOperand, findOperands, ScanDirection, isExpression, VALID_CHARS


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def convertToPyExpr(raw_expr: str) -> str:
    for index, char in enumerate(raw_expr):
        if char == '√':
            func = 'sqrt'
            sub_expr = findOperand(raw_expr, index)
            if raw_expr[sub_expr.start - 1] == '(':
                start, end = sub_expr.start - 2, sub_expr.end + 1
            else:
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


def calculate(expression: str) -> Optional[Union[int, float]]:
    if not isExpression(expression):
        print(1111)
        return None

    if expression.strip():
        return eval(convertToPyExpr(expression))


def canBeAdded(char: str, expression: str, position: int) -> bool:
    return char in VALID_CHARS


if __name__ == '__main__':
    def testExpr(text):
        print(f'Source: {text} | Py: {convertToPyExpr(text)}')

    print(convertToPyExpr('√(45^4-√(94^3-3)*45)'))
