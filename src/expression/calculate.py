from math import sqrt, pow
from typing import Union, Optional

from .utils import toEditableExpr
from .parser import RIGHT_UNARY_OPS
from .parser import findOperand, findOperands, ScanDirection
from .validation import isValidExpression

pow = pow
sqrt = sqrt


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def calculateExpr(expression: str) -> Optional[Union[int, float]]:
    if not isValidExpression(expression):
        return None

    if expression.strip():
        return eval(convertToPyExpr(expression))


def convertToPyExpr(raw_expr: str) -> str:
    in_right_part = False

    index = 0
    while index <= len(raw_expr):
        try:
            char = raw_expr[index]
        except IndexError:
            char = None

        if char in RIGHT_UNARY_OPS:
            in_right_part = True
            index += 1
            continue

        if in_right_part:
            index -= 1
            char = raw_expr[index]

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
            index += 1
            continue

        expr = f'{raw_expr[:start]}{func}({sub_expr}){raw_expr[end:]}'
        index += 1
        return convertToPyExpr(expr)
    else:
        return toEditableExpr(raw_expr)
