from enum import IntEnum
from typing import Union, Optional, Tuple

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
        if prev_char in BINARY_OPS or prev_char == '(':
            return OperationType.LeftUnary

        while not next_char:
            if next_index >= len(text):
                break

            if text[next_index] == ' ':
                next_index -= 1
            else:
                next_char = text[prev_index]

            if next_char.isdigit() and next_char in '(√':
                return OperationType.LeftUnary

    return OperationType.Binary


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

    if set(operand).intersection(ALL_OPS):
        return isValidExpression(operand)
    elif operand.startswith('0') and '.' not in operand:
        return False

    try:
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


def isValidExpression(expr: str) -> bool:
    expr = expr.strip()

    if not expr:
        return False

    if set(expr).difference(VALID_CHARS):
        return False

    if not set(expr) - (VALID_CHARS - ALL_OPS):
        return False

    bracket_counter = 0
    operand_counter = 0
    dot_counter = 0
    middle_chars_counter = 0

    in_operand = False
    operand_part = OperandPart.Left
    in_complex_middle_part = False
    complex_middle_start_pos = None
    starts_zero = False
    prev_char_is_root = False

    index = 0
    while index < len(expr):
        char = expr[index]
        # print(f'Char: {char} ; index: {index}')
        # print(f'In operand: {in_operand}')
        # print(f'Operand part: {operand_part.name}')
        # print(f'Operand counter: {operand_counter}')
        if char in BRACKETS:
            if char == '(':
                bracket_counter += 1
                if not in_operand:
                    if operand_counter != 0:
                        return False

                    in_operand = True
                    operand_part = OperandPart.Middle
                    operand_counter += 1
                else:  # if in_operand
                    if operand_part is OperandPart.Middle and not in_complex_middle_part:
                        return False

            elif char == ')':
                bracket_counter -= 1
                if in_operand:
                    if operand_part is OperandPart.Right:
                        return False

            if bracket_counter < 0:
                return False

            if bracket_counter == 1 and not in_complex_middle_part:
                complex_middle_start_pos = index
                in_complex_middle_part = True

            if bracket_counter == 0:
                in_complex_middle_part = False
                # Brackets stricted
                complex_middle_part = expr[complex_middle_start_pos + 1:index]

                if not isValidExpression(complex_middle_part):
                    return False

                operand_part = OperandPart.Right
            index += 1
            continue

        if in_operand:
            if operand_part is OperandPart.Left:
                if char in ALL_OPS:
                    if prev_char_is_root and char == '-':
                        return False
                    if char not in LEFT_UNARY_OPS:
                        return False
                elif char == ' ':
                    return False
                elif char in MIDDLE_OPERAND_PART_CHARS:
                    operand_part = OperandPart.Middle
                    middle_chars_counter = 1
                    prev_char_is_root = False
            elif operand_part is OperandPart.Middle:
                if starts_zero:
                    if char == '0':
                        starts_zero = True
                    elif char == '.':
                        starts_zero = False
                    elif char in MIDDLE_OPERAND_PART_CHARS:
                        return False

                if in_complex_middle_part:
                    index += 1
                    continue

                if char in ALL_OPS:
                    if char in ALWAYS_LEFT_UNARY:
                        return False
                    elif char in BINARY_OPS:
                        in_operand = False
                        operand_counter = 0
                    elif char in RIGHT_UNARY_OPS:
                        operand_part = OperandPart.Right
                elif char == ' ':
                    in_operand = False
                elif char in MIDDLE_OPERAND_PART_CHARS:
                    middle_chars_counter += 1

                if dot_counter == 1 and middle_chars_counter == 1:
                    return False
            elif operand_part is OperandPart.Right:
                if char in ALL_OPS:
                    if operand_part is OperandPart.Right:
                        if char in ALWAYS_LEFT_UNARY:
                            return False
                        elif char in BINARY_OPS:
                            in_operand = False
                            operand_counter = 0
                elif char == ' ':
                    in_operand = False
                elif char in MIDDLE_OPERAND_PART_CHARS:
                    return False

            if char == '.':
                if operand_part is OperandPart.Middle:
                    dot_counter += 1

                    if dot_counter > 1:
                        return False
                else:
                    return False

        else:  # not in_operand:
            if char in ALL_OPS:
                if char in LEFT_UNARY_OPS:
                    if operand_counter == 0:
                        in_operand = True
                        operand_counter += 1
                        operand_part = OperandPart.Left
                        dot_counter = 0
                        prev_char_is_root = True
                    else:
                        return False

                if char in BINARY_OPS:
                    if operand_counter == 1:
                        operand_counter = 0
                    else:
                        return False

                if char in RIGHT_UNARY_OPS:
                    return False
            elif char in MIDDLE_OPERAND_PART_CHARS:
                if char == '0':
                    starts_zero = True

                if char == '.':
                    dot_counter += 1
                elif char == ' ':
                    middle_chars_counter = 0
                else:
                    in_operand = True
                    operand_counter += 1
                    dot_counter = 0
                    operand_part = OperandPart.Middle
                    middle_chars_counter = 1

        if operand_counter > 1:
            return False

        index += 1
    #
    # print()
    # print(f'Last In operand: {in_operand}')
    # print(f'Last Operand part: {operand_part.name}')
    # print(f'Last Bracket count: {bracket_counter}')
    # print(f'Last Operand count: {operand_counter}')
    # print()

    if bracket_counter > 0:
        return False

    if operand_counter == 0:
        return False

    if operand_part is OperandPart.Left:
        return False

    if dot_counter == 1 and middle_chars_counter == 1:
        return False

    return True
