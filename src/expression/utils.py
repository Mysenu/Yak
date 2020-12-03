from enum import IntEnum

ALWAYS_LEFT_UNARY = '√'
ALWAYS_RIGHT_UNARY = '%'
LEFT_UNARY_OPS = set('-+√')
RIGHT_UNARY_OPS = set('%')
BINARY_OPS = set('+-*/^')
BRACKETS = set('()')
ALWAYS_BINARY_OPS = BINARY_OPS - (RIGHT_UNARY_OPS | LEFT_UNARY_OPS)
ALL_OPS = BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS
MIDDLE_OPERAND_PART_CHARS = set('0123456789. ') | BRACKETS
VALID_CHARS = MIDDLE_OPERAND_PART_CHARS | ALL_OPS


class ScanDirection(IntEnum):
    Left = 1
    Right = 2


class OperationType(IntEnum):
    Binary = 1
    LeftUnary = 2
    RightUnary = 3


class OperandPart(IntEnum):
    Left = 1
    Middle = 2
    Right = 3


def toEditableExpr(expression: str) -> str:
    expression = expression.replace('√', 'V')
    return expression


def fromEditableExpr(expression: str) -> str:
    expression = expression.replace('v', '√')
    return expression
