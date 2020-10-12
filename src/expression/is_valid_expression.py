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

    def __add__(self, other):
        return SubExpressionPair(self.__range, other.__range, self.subexpr, other.subexpr)

    def __str__(self):
        return self.subexpr


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


def operationType(text: str, index: int) -> Union[OperationType, bool]:
    # Todo: Что делать с пробелами?
    char = text[index]
    prev_char = text[max(index - 1, 0)]

    if char not in ALL_OPS:
        return False

    if char in ALWAYS_BINARY_OPS:
        return OperationType.Binary

    if char in ALWAYS_LEFT_UNARY:
        return OperationType.LeftUnary

    if char in ALWAYS_RIGHT_UNARY:
        return OperationType.RightUnary

    if char in LEFT_UNARY_OPS and (prev_char in BINARY_OPS or prev_char == '(' or index == 0):
        return OperationType.LeftUnary

    if char in BINARY_OPS and prev_char in (VALID_CHARS - (ALL_OPS - RIGHT_UNARY_OPS)):
        return OperationType.Binary

    return OperationType.RightUnary


def findOperand(expr: str,
                index: int,
                direction: int = ScanDirection.Right) -> Optional[SubExpression]:
    """
    Finds the range of a subexpression at the specified index and
    direction, and returns an object of the Subexpression class.
    """
    print(expr, ' | findOperand', ' | Index: ', index)
    if not expr:
        return None

    if not isOperation(expr, index):
        return None

    if direction == ScanDirection.Right:
        scan_left = False
        index += 1
        range_part = range(index, len(expr))
        open_bracket = '('
        close_bracket = ')'
    else:  # pos_expr == ScanDirection.Left:
        scan_left = True
        index -= 1
        range_part = range(index, -1, -1)
        open_bracket = ')'
        close_bracket = '('

    if index < 0 or index >= len(expr):
        return None

    start_pos = index

    if expr[index] == open_bracket:
        bracket_count = 0
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
                    start_pos = pos + 1
                    end_pos = index - 1
                else:
                    start_pos += 1
                    end_pos = pos - 1
                break
        else:
            raise SyntaxError('Unmatched bracket')
    else:
        for pos in range_part:
            # Todo: Попробовать переписать в цикл while
            char = expr[pos]
            if char in '()' or operationType(expr, pos) is OperationType.Binary:
                if scan_left:
                    start_pos = pos + 1
                    end_pos = index
                else:
                    end_pos = pos - 1
                break
        else:
            if scan_left:
                start_pos = 0
                end_pos = index
            else:
                end_pos = len(expr) - 1

    if direction == ScanDirection.Right:
        sub_range = start_pos, end_pos + 1
        print(expr[start_pos:end_pos + 1], 'Right')
    else:  # ScanDirection.Left
        sub_range = start_pos, end_pos + 1
        print(expr[start_pos:end_pos + 1], 'Left')
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
    if isinstance(operand, SubExpression):
        operand = str(operand)

    if operand is None:
        return None

    try:
        float(operand)
        return True
    except ValueError:
        return None if set(operand).intersection(ALL_OPS) else False


def isValidOperation(expr: str, index: int) -> Optional[bool]:
    print(expr, ' | isValidOperation: ', expr, 'Index: ', index)

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

    print(expr, ' | isValidOperation: ', operands)
    return all(operands)


def isExpression(text: str) -> bool:
    if not text:
        return False

    # Проверяем на наличие невалидных символов
    if set(text) - VALID_CHARS:
        return False

    # Проверяем на присутствие операций
    if not (set(text) - (VALID_CHARS - ALL_OPS)):
        return False
    # TODO: Упростить написание через метод

    operand_count = 0
    bracket_count = 0
    first_operand = False

    try:
        index = 0
        while index < len(text):
            char = text[index]

            if isOperation(text, index):
                if isValidOperation(text, index) is not True:
                    print('isExpression: ', text[index])
                    return False
                if operationType(text, index) is OperationType.Binary:
                    first_operand = False
                    operand_count = 0
            elif char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
            elif char == ' ' and text[max(index - 1, 0)].isdigit():
                first_operand = True
                operand_count += 1
                if operand_count > 1:
                    print('False operand count 1')
                    return False
            elif char == ' ':
                pass

            if char.isdigit() and first_operand:
                operand_count += 1
                if operand_count > 1:
                    return False

            if bracket_count < 0:
                print('False bracket count')
                return False
            index += 1
    except SyntaxError:
        print('False syntaxError')
        return False

    if bracket_count != 0:
        print('False bracket count')
        return False

    return True


# print(isExpression('√48-1+3'))
# print(isExpression('√9'))
# print(findOperands('1+(45-3)^(34*4)-8', 8))
# print(isExpression('45'))
print(operationType('43+(--9)+√5', 5))
