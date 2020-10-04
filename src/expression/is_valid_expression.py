from typing import Union, Optional

from src.expression.expressions import ScanDirection, SubExpression, SubExpressions


LEFT_UNARY_OPS = set('-+√')
RIGHT_UNARY_OPS = set('%')
BINARY_OPS = set('+-*/^')
ALWAYS_BINARY_OPS = set('*/^')
ROOT_OP = '√'
PROCENT_OP = '%'
ALL_OPS = BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS
VALID_CHARS = set('0123456789+-/*.()√^% ')


def findOperand(expr: str,
                index: int,
                direction: int = ScanDirection.Right) -> Union[SubExpression, None]:
    """
    Finds the range of a subexpression at the specified index and
    direction, and returns an object of the Subexpression class.
    """
    print(expr, ' | findOperand', ' | Index: ', index)
    if not expr:
        return

    if direction == ScanDirection.Right:
        scan_left = False
        index += 1
        expr_part = expr[index:]
        open_bracket = '('
        close_bracket = ')'
    else:  # pos_expr == ScanDirection.Left:
        scan_left = True
        expr_part = expr[:index][::-1]
        index -= 1
        open_bracket = ')'
        close_bracket = '('
    start_pos = index
    if expr[index] == open_bracket:
        bracket_count = 0
        if scan_left:
            index = -index
        for pos, char in enumerate(expr_part, index):
            if char == open_bracket:
                bracket_count += 1
            elif char == close_bracket:
                bracket_count -= 1

            if bracket_count < 0:
                raise SyntaxError('Unmatched bracket')

            if bracket_count == 0:
                if scan_left:
                    start_pos = pos + 1
                    end_pos = -(index + 1)
                    print(start_pos, end_pos, 'Hey')
                else:
                    end_pos = pos - 1
                break
        else:
                raise SyntaxError('Unmatched bracket')
    else:
        if scan_left:
            index = -index
        for pos, char in enumerate(expr_part, index):
            if char in '()':
                if scan_left:
                    end_pos = pos + 1
                else:
                    end_pos = pos - 1
                break

            if isOperation(expr, pos):
                if isBinaryOperation(expr, pos):
                    if scan_left:
                        end_pos = pos + 1
                    else:
                        end_pos = pos - 1
                    break
        else:
            if scan_left:
                end_pos = pos + 1
            else:
                end_pos = pos - 1

    if direction == ScanDirection.Right:
        sub_range = start_pos, end_pos + 1
        print(expr[start_pos:end_pos + 1], 'Right')
    else:  # ScanDirection.Left
        sub_range = start_pos, end_pos + 1
        print(start_pos, end_pos + 1, 'Left')
        print(expr[start_pos:end_pos + 1], 'Left')
    return SubExpression(sub_range, expr)


def findOperands(expr: str, index: int) -> SubExpressions:
    left_part = findOperand(expr, index, ScanDirection.Left)
    right_part = findOperand(expr, index, ScanDirection.Right)
    return left_part + right_part


def isOperation(text: str, index: int) -> bool:
    return text[index] in ALL_OPS


def isBinaryOperation(text: str, index: int) -> bool:
    if text[index] in ALWAYS_BINARY_OPS:
        return True
    # Проверяем операцию на унарность с помощью предыдущего символа
    print(text, ' | ', 'isBinaryOperation: ', text[index], ' | Index: ', index)
    if index == 0 or text[index - 1] in BINARY_OPS | LEFT_UNARY_OPS or text[index] in RIGHT_UNARY_OPS:
        print(text, ' | ', 'isBinaryOperation: Not', ' | Index: ', index)
        return False
    # Если условия не выполнены, то операция бинарная
    print(text, ' | ', 'isBinaryOperation: Yes', ' | Index: ', index)
    return True


def isValidOperand(operand: Union[str, SubExpression]) -> Optional[bool]:
    if isinstance(operand, SubExpression):
        operand = str(operand)

    try:
        float(operand)
        return True
    except ValueError:
        return None if set(operand).intersection(ALL_OPS) else False


def isValidOperation(text: str, index: int) -> bool:
    print(text, ' | isValidOperation: ', text, 'Index: ', index)
    try:
        if isBinaryOperation(text, index):
            left_operand, right_operand = findOperands(text, index)
            print(text, ' | isValidOperation: ', left_operand, right_operand)
            operands = isValidOperand(left_operand), isValidOperand(right_operand)
        else:
            if text[index] in LEFT_UNARY_OPS:
                operand = findOperand(text, index, ScanDirection.Right)
            else:
                operand = findOperand(text, index, ScanDirection.Left)
            print(text, ' | isValidOperation: ', operand)
            operands = isValidOperand(operand),
    except IndexError:
        return False

    if False in operands:
        print('lol')
        return False
    if None in operands:
        return None
    return True


def isExpression(text: str) -> bool:
    if not text:
        return False

    # Проверяем на наличие невалидных символов
    if set(text) - VALID_CHARS:
        return False

    operation_count = 0
    char_is_digit = False
    char_is_procent = False

    try:
        index = 0
        while index < len(text):
            char = text[index]
            if char == ROOT_OP and char_is_digit:
                return False

            if char.isdigit() and char_is_procent:
                return False

            if char.isdigit():
                char_is_digit = True
            else:
                char_is_digit = False

            if char == PROCENT_OP:
                char_is_procent = True
            else:
                char_is_procent = False

            if isOperation(text, index):
                operation_count += 1
                if isValidOperation(text, index) is False:
                    print('isExpression: ', text[index])
                    return False
            index += 1
    except SyntaxError:
        return False

    if operation_count < 1:
        return False

    return True
# print(isExpression('√(48-1)'))
print(isExpression('(8-1)+(63+3)'))
