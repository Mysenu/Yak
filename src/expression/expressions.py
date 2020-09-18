from typing import Optional, Union


def prepareExpression(expression: str, change_math_char=False) -> str:
    invalid_characters = '+-/*.√^% '

    expression = expression.rstrip('/*-+. ')

    if not change_math_char:
        return expression

    converted_expression = convertToPyExpr(expression)

    return converted_expression


class ScanDirection:
    Left = 0b10
    Right = 0b01


class SubExpression:
    def __init__(self):
        self.subexpression_location = ()
        self.part_expression = ()

    def addLocation(self, value):
        if not value:
            return

        self.subexpression_location = value

    def addPart(self, value):
        if not value:
            return

        self.part_expression = value


def findExpressionPart(expr: str,
                       start: int,
                       direction: int = ScanDirection.Right):
    if not expr:
        return

    if direction == ScanDirection.Right:
        start += 1
        part_expr = expr[start:]
        open_bracket = '('
        close_bracket = ')'
    else:  # pos_expr == ScanDirection.Left:
        start -= 1
        part_expr = expr[:start + 1][::-1]
        open_bracket = ')'
        close_bracket = '('

    src_char = expr[start]
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
            if not char.isdigit() and char != '.':
                rel_end_pos = rel_pos
                break
        else:
            rel_end_pos = len(part_expr)
    if direction == ScanDirection.Right:
        part = expr[start:start + rel_end_pos]
        expr_section = [start, start + rel_end_pos]
    else:
        part = expr[start - rel_end_pos + 1:start + 1]
        expr_section = [start - rel_end_pos + 1, start + 1]

    part_expr = SubExpression()
    part_expr.addLocation(expr_section)
    part_expr.addPart(part)
    return part_expr


def findExpressionParts(expr: str, index: int):
    left_part = findExpressionPart(expr, index, ScanDirection.Left)
    start, _ = left_part.subexpression_location

    right_part = findExpressionPart(expr, index, ScanDirection.Right)
    _, end = right_part.subexpression_location

    subexpression = SubExpression
    subexpression.subexpression_location = start, end
    subexpression.part_expression = left_part.part_expression, right_part.part_expression
    return subexpression


def convertToPyExpr(r_expr: str) -> str:
    math_char = '+-/*^'

    r_expr = r_expr.replace(' ', '')

    for index, char in enumerate(r_expr):
        if char == '√':
            dict_expr = findExpressionPart(r_expr, index, ScanDirection.Right)
            start, end = dict_expr['expr_section']
            part_expr = ''.join(dict_expr['expr'])
            expr = f'{r_expr[:start - 1]}sqrt({part_expr}){r_expr[end:]}'
            return convertToPyExpr(expr)
    else:
        return r_expr


def isExpression(text: str) -> bool:
    if not text:
        return False

    valid_chars = '+-*/^'
    math_char_count = 0
    math_char = False
    is_valid = False
    for index, char in enumerate(text):
        if math_char and not (char.isdigit() or char in '().'):
            is_valid = False
        else:
            is_valid = True
            math_char = False

        if char in valid_chars:
            math_char_count += 1
            math_char = True

        if math_char and len(text) == (index + 1):
            is_valid = False
        elif not math_char and len(text) == (index + 1) and math_char_count == 0:
            is_valid = False
        else:
            is_valid = True

    return is_valid


def isIdenticalExpressions(expr1: str, expr2: str) -> bool:
    return expr1.split(' ') == expr2.split(' ')


def calculate(expression: str) -> Optional[Union[int, float, bool]]:
    if expression.strip():
        expression = prepareExpression(expression, True)
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
    # print(findPartExpression('2+(344^4)+√4233', 6), '|||', '2+(344^4)+√4233')
    # print(findPartExpression('2+344^4+√4233', 5), '|||', '2+(344^4)+√4233')
    # print(findPartExpression('2+344^4+(√4233)', 9, ScanDirection.Right), '|||', '2+(344^4)+√4233')
    # print(findPartExpression('√2+344^4+√4233', 0, ScanDirection.Right), '|||', '√2+(344^4)+√4233')
    # print(findPartExpression('2+344^4+√4233', 5, ScanDirection.Left), '|||', '2+(344^4)+√4233')
    # print(findExpressionPart('2+(344^4)+√4233', 6, ScanDirection.Left), '|||', '2+(344^4)+√4233')
    # print(findPartExpression('2+(344^4)+√4233', 10, ScanDirection.Right), '|||', '2+(344^4)+√4233')
    # print(findExpressionParts('22^32+2(23^34)2+42^33', 10))
    sub = findExpressionPart('22^32+√(2234+23)+42^33', 6)
    print(sub.part_expression, sub.subexpression_location)
