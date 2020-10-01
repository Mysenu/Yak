from typing import Union

from src.expression.expressions import ScanDirection, SubExpression, SubExpressions


LEFT_UNARY_OPS = set('-+√')
RIGHT_UNARY_OPS = set('%')
BINARY_OPS = set('+-*/^')
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

            if bracket_count < 0:
                raise SyntaxError('Unmatched bracket')

            if bracket_count == 0:
                # Обрезаем скобки
                index += 1
                rel_end_pos = rel_pos - 1
                break
        else:
            if bracket_count == 0:
                # Обрезаем скобки
                index += 1
                rel_end_pos = len(part_expr) - 2
            else:
                raise SyntaxError('Unmatched bracket')
    else:
        for rel_pos, char in enumerate(part_expr):
            if char in LEFT_UNARY_OPS | RIGHT_UNARY_OPS | BINARY_OPS:
                if isBinaryOperation(expr, len(expr) - len(part_expr) + rel_pos):
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


def findOperands(expr: str, index: int) -> SubExpressions:
    left_part = findOperand(expr, index, ScanDirection.Left)
    right_part = findOperand(expr, index, ScanDirection.Right)
    return left_part + right_part


def isOperation(text: str, index: int) -> bool:
    return text[index] in BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS


'''
isValidOperand
isValidBinaryOperation
isValidUnaryOperation
isBinaryOperation
isValidOperation
'''


def isBinaryOperation(text: str, index: int) -> bool:
    # Проверяем операцию на унарность с помощью предыдущего символа
    print(text, ' | ', 'isBinaryOperation: ', text[index], ' | Index: ', index)
    if index == 0 or text[index - 1] in BINARY_OPS | LEFT_UNARY_OPS or text[index] in RIGHT_UNARY_OPS:
        print(text, ' | ', 'isBinaryOperation: No', ' | Index: ', index)
        return False
    # Если условия не выполнены, то операция бинарная
    print(text, ' | ', 'isBinaryOperation: Yes', ' | Index: ', index)
    return True


def isValidOperand(operand: str) -> bool:
    for char in operand:
        if char in BINARY_OPS | LEFT_UNARY_OPS | RIGHT_UNARY_OPS:
            return isExpression(operand)
    else:
        try:
            if float(operand):
                return True
        except ValueError:
            return False


def isValidOperation(text: str, index: int) -> bool:
    print(text, ' | isValidOperation: ', text, 'Index: ', index)
    if isBinaryOperation(text, index):
        left_operand, right_operand = findOperands(text, index).subexprs
        print(text, ' | isValidOperation: ', left_operand, right_operand)
        return isValidOperand(left_operand) and isValidOperand(right_operand)
    else:
        if text[index] in LEFT_UNARY_OPS:
            operand = findOperand(text, index, ScanDirection.Right).subexpr
        else:
            operand = findOperand(text, index, ScanDirection.Left).subexpr
        print(text, ' | isValidOperation: ', operand)
        return isValidOperand(operand)


def isExpression(text: str) -> bool:
    if not text:
        return False

    # Проверяем на наличие невалидных символов
    if set(text) - VALID_CHARS:
        return False

    try:
        index = 0
        while index < len(text):
            if isOperation(text, index):
                if not isValidOperation(text, index):
                    print('isExpression: ', text[index])
                    return False
            index += 1
    except SyntaxError:
        return False
    return True
# print(isExpression('√(48-1)'))
print(isExpression('√-(1-2)'))