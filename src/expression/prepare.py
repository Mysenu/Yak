from src.expression.check import RIGHT_UNARY_OPS, findOperand, findOperands, ScanDirection


def findClosingBracket(expr: str, index: int = 0):
    if not expr:
        print('Not expr')
        return

    if expr[index] != '(':
        print('Not bracket - ', expr[index])
        return

    bracket_count = 1
    for pos, char in enumerate(expr[index + 1:], index + 1):
        if char == ')':
            bracket_count -= 1

        if char == '(':
            bracket_count += 1

        if bracket_count == 0:
            return pos


def findOperandEnd(expr: str, start: int = 0) -> int:
    dot_count = 0
    for pos, char in enumerate(expr[start + 1:], start + 1):
        if char == '.':
            if dot_count == 0:
                dot_count += 1
            else:
                return pos - 1

        if len(expr) == (pos + 1):
            return pos

        if not char.isdigit() and char != '.' and char != '√':
            return pos - 1


def convertToPyExpr_2(expr: str) -> str:
    operators = {
        '^': 'pow',
        '√': 'sqrt'
    }

    pos = 0
    while pos < len(expr):
        if expr[pos] not in operators:
            pos += 1
            continue

        operator = expr[pos]
        char = expr[pos + 1]
        if char == '(':
            start = pos
            end = findClosingBracket(expr, start + 1) + 1
            sub_exp = expr[start + 2:end - 1]
        else:
            start = pos
            end = findOperandEnd(expr, start) + 1
            sub_exp = expr[start + 1:end]
        pos += 1

        if sub_exp:
            expr = f'{expr[:start]}{operators[operator]}({sub_exp}){expr[end:]}'

            
def toEditableExpr(expression: str) -> str:
    expression = expression.replace('√', 'V')
    return expression


def fromEditableExpr(expression: str) -> str:
    expression = expression.replace('v', '√')
    return expression


def convertToPyExpr(raw_expr: str) -> str:
    in_right_part = False

    index = 0
    while index <= len(raw_expr):
        try:
            char = raw_expr[index]
        except IndexError:
            char = None

        if char in RIGHT_UNARY_OPS:
            in_right_part = True
            index += 1
            continue

        if in_right_part:
            index -= 1
            char = raw_expr[index]

        if char == '√':
            func = 'sqrt'
            sub_expr = findOperand(raw_expr, index)
            if raw_expr[sub_expr.start - 1] == '(':
                start, end = sub_expr.start - 2, sub_expr.end + 1
            else:
                start, end = sub_expr.start - 1, sub_expr.end
        elif char == '^':
            func = 'pow'
            sub_expr = findOperands(raw_expr, index)
            start, end = sub_expr.start, sub_expr.end
        elif char == '%':
            func = 'toPercent'
            sub_expr = findOperand(raw_expr, index, ScanDirection.Left)
            start, end = sub_expr.start, sub_expr.end + 1
        else:
            index += 1
            continue

        expr = f'{raw_expr[:start]}{func}({sub_expr}){raw_expr[end:]}'
        index += 1
        return convertToPyExpr(expr)
    else:
        return raw_expr
