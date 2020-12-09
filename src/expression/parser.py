from enum import IntEnum
from typing import Optional

from .subexpression import SubExpression, SubExpressionPair


ALWAYS_LEFT_UNARY = '√'
ALWAYS_RIGHT_UNARY = '%'
LEFT_UNARY_OPS = set('-+√')
RIGHT_UNARY_OPS = set('%')
BINARY_OPS = set('+-*×/^')
BRACKETS = set('()')
ALWAYS_BINARY_OPS = BINARY_OPS - (RIGHT_UNARY_OPS | LEFT_UNARY_OPS)
ALL_OPS = BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS
MIDDLE_OPERAND_PART_CHARS = set('0123456789. ') | BRACKETS
VALID_CHARS = MIDDLE_OPERAND_PART_CHARS | ALL_OPS


def isOperation(text: str, index: int) -> bool:
    return text[index] in ALL_OPS


class OperationType(IntEnum):
    Binary = 1
    LeftUnary = 2
    RightUnary = 3


def operationType(text: str, index: int) -> Optional[OperationType]:
    char = text[index]

    if char not in ALL_OPS:
        return None

    if char in ALWAYS_BINARY_OPS:
        return OperationType.Binary

    if char in ALWAYS_LEFT_UNARY:
        return OperationType.LeftUnary

    if char in ALWAYS_RIGHT_UNARY:
        return OperationType.RightUnary

    prev_index = index - 1
    prev_char = None
    next_index = index + 1
    next_char = None
    while not prev_char:
        if prev_index < 0:
            break

        if text[prev_index] == ' ':
            prev_index -= 1
        else:
            prev_char = text[prev_index]

    if char in BINARY_OPS:
        if prev_char in VALID_CHARS - (ALL_OPS - RIGHT_UNARY_OPS) - set('('):
            return OperationType.Binary

    if char in LEFT_UNARY_OPS:
        if prev_char in BINARY_OPS or prev_char in (set(ALWAYS_LEFT_UNARY) | BRACKETS):
            return OperationType.LeftUnary

        while not next_char:
            if next_index >= len(text):
                break

            if text[next_index] == ' ':
                next_index -= 1
            else:
                next_char = text[prev_index]

            if next_char.isdigit() and next_char in (set(ALWAYS_LEFT_UNARY) | BRACKETS):
                return OperationType.LeftUnary

    return OperationType.Binary


class ScanDirection(IntEnum):
    Left = 1
    Right = 2


def findOperand(expr: str,
                start_index: int,
                direction: int = ScanDirection.Right) -> Optional[SubExpression]:
    """
    Finds the range of a subexpression at the specified index and
    direction, and returns an object of the Subexpression class.
    """
    if not expr:
        return None

    if not isOperation(expr, start_index):
        return None

    if direction == ScanDirection.Right:
        scan_left = False
        start_index += 1
        range_part = range(start_index, len(expr))
        open_bracket = '('
        close_bracket = ')'
    else:  # pos_expr == ScanDirection.Left:
        scan_left = True
        start_index -= 1
        range_part = range(start_index, -1, -1)
        open_bracket = ')'
        close_bracket = '('

    expr_len = len(expr)

    if start_index < 0 or start_index >= expr_len:
        return None

    start_pos = start_index
    abs_pos = start_index
    with_unary_op = True

    while expr[abs_pos] in (ALWAYS_RIGHT_UNARY + ALWAYS_LEFT_UNARY) or expr[abs_pos] == ' ':
        if direction == ScanDirection.Right:
            abs_pos += 1
        else:
            abs_pos -= 1

        if abs_pos > expr_len or abs_pos < 0:
            return None

        range_part = range(abs_pos, expr_len)

        if direction == ScanDirection.Left:
            range_part = range(abs_pos, -1, -1)

        with_unary_op = True

    if expr[abs_pos] == open_bracket:
        bracket_count = 0
        removed_brackets = 1

        if with_unary_op:
            removed_brackets = 0

        for pos in range_part:
            char = expr[pos]
            if char == open_bracket:
                bracket_count += 1
            elif char == close_bracket:
                bracket_count -= 1

            if bracket_count < 0:
                raise SyntaxError('Unmatched bracket')

            if bracket_count == 0:
                if scan_left:
                    start_pos = pos + removed_brackets
                    end_pos = abs_pos - removed_brackets
                else:
                    start_pos += removed_brackets
                    end_pos = pos - removed_brackets
                break
        else:
            raise SyntaxError('Unmatched bracket')
    else:
        for pos in range_part:
            char = expr[pos]
            if char in '()' or operationType(expr, pos) is OperationType.Binary:
                if scan_left:
                    start_pos = pos + 1
                    end_pos = start_index
                else:
                    end_pos = pos - 1
                break
        else:
            if scan_left:
                start_pos = 0
                end_pos = start_index
            else:
                end_pos = expr_len - 1

    if direction == ScanDirection.Right:
        sub_range = start_pos, end_pos + 1
    else:  # ScanDirection.Left
        sub_range = start_pos, end_pos + 1
    return SubExpression(sub_range, expr)


def findOperands(expr: str, index: int) -> Optional[SubExpressionPair]:
    if index < 0 or index >= len(expr):
        return None

    left_part = findOperand(expr, index, ScanDirection.Left)
    right_part = findOperand(expr, index, ScanDirection.Right)

    if None in (left_part, right_part):
        return None

    return left_part + right_part
