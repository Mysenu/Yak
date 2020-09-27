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
        self.__range = min(range_1[0], range_2[0]), max(range_1[1], range_2[1])
        self.__subexprs = subexpr_1, subexpr_2

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
                rel_end_pos = rel_pos
                break
        else:
            rel_end_pos = len(part_expr) - 1
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
    print(expr[sub_range[0]:sub_range[1]])
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


def isExpression(text: str) -> bool:
    LEFT_UNARY_OPS = '-+√'
    RIGHT_UNARY_OPS = '%'
    BINARY_OPS = '+-*/^'

    if not text:
        return False

    is_expression = True
    op_char_found = False  # Todo: Rename
    dot_found = False

    for index, char in enumerate(text):
        if index == 0 and char in LEFT_UNARY_OPS:
            continue

        if char in BINARY_OPS:
            op_char_found = True

        if op_char_found and char.isdigit():
            is_expression = True
            continue

        if char in RIGHT_UNARY_OPS:
            is_expression = True

        if char.isdigit() or char in '()':
            continue

        if len(text) == index + 1 and op_char_found:
            return False

        if char == '.':
            if dot_found:
                return False
            else:
                dot_found = True

    return is_expression


def calculate(expression: str) -> Optional[Union[int, float, bool]]:
    if expression.strip():
        expression = prepareExpression(expression, True)
        return eval(expression)


def canBeAdded(char: str, expression: str, position: int) -> bool:
    valid_char = '0123456789+-/*.()√^% '
    return char in valid_char


if __name__ == '__main__':
    def testExpr(text):
        print(f'Source: {text} | Py: {convertToPyExpr(text)} | Valid: {isExpression(text)}')
    # print(calculate('(11-8)^(3-1)'))
    # print(calculate('√(45+4)'))
    # print(calculate('30*45%'))
    # testExpr('√4+23')
    # testExpr('4+23')
    # testExpr('4')
    # testExpr('4+(1+3)')
    # testExpr('+4')
    # testExpr('4%')
    # testExpr('++++4')
    # testExpr('4++')
    # testExpr('√4+√4')
    # testExpr('(-4+5)-3')
    # testExpr('4+4.4.4')
    # testExpr('.5+.5')
    # testExpr('√√4')
    # testExpr('√(-√4)')
    # testExpr('4^4')
    # testExpr('-(4+1)')
    # testExpr('4.4+4.4')
    # testExpr('√√')
    # testExpr('4+4()')
    # testExpr('')
    print(convertToPyExpr('√(4+1)%'))
    print(convertToPyExpr('√4+1%'))
    print(convertToPyExpr('√(4+1)'))
    print(convertToPyExpr('4+√5'))