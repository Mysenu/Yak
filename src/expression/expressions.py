from typing import Optional, Union, Tuple
from enum import IntEnum
from math import sqrt, pow


def prepareExpression(expression: str, change_math_char=False) -> str:
    converted_expression = convertToPyExpr(expression)
    return converted_expression


class ScanDirection(IntEnum):
    Left = 1
    Right = 2


class SubExpression:
    """The class is implemented as an object for ease of working with subexpression and their range."""
    def __init__(self, range: tuple = (0, 0), expr: str = '') -> None:
        self.__range = range
        self.__expr = expr

    @property
    def range(self) -> Tuple[int, int]:
        return self.__range

    @property
    def expr(self) -> str:
        return self.__expr

    @property
    def start(self) -> int:
        return self.__range[0]

    @property
    def end(self) -> int:
        return self.__range[1]

    @property
    def subexpr(self) -> str:
        start, end = self.__range
        return self.__expr[start:end]

    def __add__(self, other):
        return SubExpressions(self.__range, other.__range, self.subexpr, other.subexpr)

    def __str__(self):
        return f'{self.subexpr}'


class SubExpressions:
    """The class is implemented as an object for ease of working with subexpressions and their ranges."""
    def __init__(self, range_1: tuple, range_2: tuple, subexpr_1: str, subexpr_2: str) -> None:
        self.__subexprs = subexpr_1, subexpr_2
        self.__range = min(range_1[0], range_2[0]), max(range_1[1], range_2[1])

    @property
    def range(self) -> Tuple[int, int]:
        return self.__range

    @property
    def subexprs(self) -> Tuple[str, str]:
        return self.__subexprs

    @property
    def start(self) -> int:
        return self.__range[0]

    @property
    def end(self) -> int:
        return self.__range[1]

    def __str__(self) -> str:
        return ', '.join(self.__subexprs)


def findExpressionPart(expr: str,
                       index: int,
                       direction: int = ScanDirection.Right) -> Union[SubExpression, None]:
    """
    Finds the range of a subexpression at the specified index and
    direction, and returns an object of the Subexpression class.
    """
    if not expr:
        return

    if direction == ScanDirection.Right:
        index += 1
        part_expr = expr[index:]
        open_bracket = '('
        close_bracket = ')'
    else:  # pos_expr == ScanDirection.Left:
        index -= 1
        part_expr = expr[:index + 1][::-1]
        open_bracket = ')'
        close_bracket = '('

    src_char = expr[index]
    if src_char == '(' or src_char == ')':
        bracket_count = 0
        for rel_pos, char in enumerate(part_expr):
            if char == open_bracket:
                bracket_count += 1
            elif char == close_bracket:
                bracket_count -= 1

            if bracket_count == 0:
                rel_end_pos = rel_pos + 1
                break
        else:
            rel_end_pos = len(part_expr)
    else:
        for rel_pos, char in enumerate(part_expr):
            if not char.isdigit() and char != '.' and char != '√':
                rel_end_pos = rel_pos
                break
        else:
            rel_end_pos = len(part_expr)

    if direction == ScanDirection.Right:
        sub_range = index, index + rel_end_pos
    else:
        index += 1
        sub_range = index - rel_end_pos, index

    return SubExpression(sub_range, expr)


def findExpressionParts(expr: str, index: int) -> SubExpressions:
    left_part = findExpressionPart(expr, index, ScanDirection.Left)
    right_part = findExpressionPart(expr, index, ScanDirection.Right)
    return left_part + right_part


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def convertToPyExpr(raw_expr: str) -> str:
    for index, char in enumerate(raw_expr):
        if char == '√':
            func = 'sqrt'
            sub_expr = findExpressionPart(raw_expr, index)
            start, end = sub_expr.start - 1, sub_expr.end
        elif char == '^':
            func = 'pow'
            sub_expr = findExpressionParts(raw_expr, index)
            start, end = sub_expr.start, sub_expr.end
        elif char == '%':
            func = 'toPercent'
            sub_expr = findExpressionPart(raw_expr, index, ScanDirection.Left)
            start, end = sub_expr.start, sub_expr.end + 1
        else:
            continue

        expr = f'{raw_expr[:start]}{func}({sub_expr}){raw_expr[end:]}'
        return convertToPyExpr(expr)
    else:
        return raw_expr


# def isExpression(expression: str) -> bool:
#     first_math_char = '+-*/^'
#     second_math_char = '%√'
#     is_expression = False
#     math_char = False
#     point = False
#     for index, char in enumerate(expression):
#         if (char in first_math_char or char in second_math_char) and index == 0:  # исключаем +/- числа
#             continue
#
#         if char.isdigit() and math_char:
#             is_expression = True
#             continue
#
#         if char.isdigit():
#             continue
#
#         if len(expression) == index + 1 and math_char:
#             is_expression = False
#             break
#
#         if char == '.' and point:
#             is_expression = False
#             break
#
#         if char == '.':
#             point = True
#
#     else:
#         if not is_expression:
#             return False
#         return True


def isIdenticalExpressions(expr1: str, expr2: str) -> bool:
    return expr1.split(' ') == expr2.split(' ')


def calculate(expression: str) -> Optional[Union[int, float, bool]]:
    if expression.strip():
        expression = prepareExpression(expression, True)
        print(expression)
        return eval(expression)


def canBeAdded(char: str, expression: str, position: int) -> bool:
    valid_char = '0123456789+-/*.()√^% '
    start_and_any_quantity = '123456789(+-.√'
    middle_and_always_one = '%√^/*-+. '

    if position == 0 or not expression:
        last_char = ''
    else:
        last_char = expression[position - 1]

    if not expression and char in start_and_any_quantity:
        return True
    elif expression == '0' and char == '0':
        return False
    elif last_char in middle_and_always_one and char in middle_and_always_one:
        return False
    elif expression and char in valid_char:
        return True


if __name__ == '__main__':
    print(calculate('(11-8)^(3-1)'))
    print(calculate('√(45+4)'))
    print(calculate('30*45%'))
