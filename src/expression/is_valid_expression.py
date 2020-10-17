from enum import IntEnum
from typing import Union, Optional, Tuple

ALWAYS_LEFT_UNARY = '√'
ALWAYS_RIGHT_UNARY = '%'
LEFT_UNARY_OPS = set('-+√')
RIGHT_UNARY_OPS = set('%')
BINARY_OPS = set('+-*/^')
ALWAYS_BINARY_OPS = BINARY_OPS - (RIGHT_UNARY_OPS | LEFT_UNARY_OPS)
ALL_OPS = BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS
VALID_CHARS = set('0123456789. ') | ALL_OPS | set('()')


class ScanDirection(IntEnum):
    Left = 1
    Right = 2


class OperationType(IntEnum):
    Binary = 1
    LeftUnary = 2
    RightUnary = 3


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

    def __add__(self, other) -> 'SubExpressionPair':
        return SubExpressionPair(self.__range, other.__range, self.subexpr, other.subexpr)

    def __str__(self) -> str:
        return self.subexpr

    def __bool__(self) -> bool:
        return bool(min(len(self.__range), len(self.__expr)))


class SubExpressionPair:
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

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> str:
        return self.__subexprs[index]


def isOperation(text: str, index: int) -> bool:
    return text[index] in ALL_OPS


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
    while not prev_char:
        if prev_index < 0:
            break

        if text[prev_index] == ' ':
            prev_index -= 1
        else:
            prev_char = text[prev_index]

    if char in LEFT_UNARY_OPS:
        if prev_char in BINARY_OPS or prev_char == '(' or prev_char is None:
            return OperationType.LeftUnary

    if char in BINARY_OPS:
        if prev_char in VALID_CHARS - (ALL_OPS - RIGHT_UNARY_OPS) - set('('):
            return OperationType.Binary

    return OperationType.RightUnary


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

    while expr[abs_pos] in (ALWAYS_RIGHT_UNARY + ALWAYS_LEFT_UNARY):
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


def isValidOperand(operand: Union[str, SubExpression]) -> Optional[bool]:
    if not operand:
        return None

    if isinstance(operand, SubExpression):
        operand = str(operand)

    first_point = False
    if operand[0] == '0':
        for char in operand:
            if char == '.':
                first_point = True
            elif char == '.' and first_point:
                return False

            if char == '0' and not first_point:
                continue
            elif not first_point:
                return False
        else:
            if first_point:
                return True
            return False

    try:
        # Удаление всех операций из операнда
        if set(operand).intersection(ALL_OPS):
            return isExpression(operand)
        float(operand)
        return True
    except ValueError:
        return False


def isValidOperation(expr: str, index: int) -> Optional[bool]:
    operation_type = operationType(expr, index)

    if operation_type == OperationType.Binary:
        result = findOperands(expr, index)
    elif operation_type == OperationType.RightUnary:
        result = findOperand(expr, index, ScanDirection.Left)
    elif operation_type == OperationType.LeftUnary:
        result = findOperand(expr, index, ScanDirection.Right)
    else:
        return None

    if result is None:
        return None

    if operation_type == OperationType.Binary:
        operands = map(isValidOperand, result)
    else:
        operands = isValidOperand(result),

    return all(operands)


def isExpression(text: str) -> bool:
    if not text:
        return False

    # Проверяем на наличие невалидных символов
    if set(text).difference(VALID_CHARS):
        return False

    # Проверяем на присутствие операций
    if not set(text) - (VALID_CHARS - ALL_OPS):
        return False

    operand_count = 0
    bracket_count = 0
    first_operand = False

    try:
        index = 0
        while index < len(text):
            char = text[index]
            if char in ALWAYS_LEFT_UNARY and text[max(index - 1, 0)].isdigit():
                return False
            elif char in ALWAYS_RIGHT_UNARY and text[min(index + 1, len(text) - 1)].isdigit():
                return False
            elif isOperation(text, index):
                if isValidOperation(text, index) is not True:
                    return False
                if operationType(text, index) is OperationType.Binary:
                    first_operand = False
                    operand_count = 0
            elif char == '(' and text[max(index - 1, 0)].isdigit():
                return False
            elif char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
            elif char == ' ' and text[max(index - 1, 0)].isdigit():
                first_operand = True
                operand_count += 1
                if operand_count > 1:
                    return False
            elif char == ' ':
                pass

            if char.isdigit() and first_operand:
                operand_count += 1
                if operand_count > 1:
                    return False

            if bracket_count < 0:
                return False
            index += 1
    except SyntaxError:
        return False

    if bracket_count != 0:
        return False

    return True


