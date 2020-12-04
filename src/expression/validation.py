from enum import IntEnum

from .parser import ALWAYS_LEFT_UNARY, LEFT_UNARY_OPS, RIGHT_UNARY_OPS, BINARY_OPS, BRACKETS, ALL_OPS, \
    MIDDLE_OPERAND_PART_CHARS, VALID_CHARS


class OperandPart(IntEnum):
    Left = 1
    Middle = 2
    Right = 3


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
