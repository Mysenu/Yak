from typing import Optional, Union
from math import sqrt, pow

from src.expression.is_valid_expression import findOperand, findOperands, ScanDirection, isValidExpression, VALID_CHARS
from is_valid_expression import RIGHT_UNARY_OPS


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def convertToPyExpr(raw_expr: str) -> str:
    index = 0
    step_counter = 0

    while index < len(raw_expr):
        char = raw_expr[index]
        next_char = None

        if index + 1 < len(raw_expr):
            next_char = raw_expr[index + 1]

        if char in RIGHT_UNARY_OPS:
            index += 1
            if next_char:
                step_counter += 1
                continue

        if step_counter:
            step_counter -= 1
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
        return raw_expr


def calculate(expression: str) -> Optional[Union[int, float]]:
    if not isValidExpression(expression):
        return None

    if expression.strip():
        return eval(convertToPyExpr(expression))


def canBeAdded(char: str, expression: str, position: int) -> bool:
    return char in VALID_CHARS


if __name__ == '__main__':
    def testExpr(text):
        print(f'Source: {text} | Py: {convertToPyExpr(text)}')
