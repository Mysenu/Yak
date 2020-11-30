from typing import Union, Optional

from src.expression.check import isValidExpression
from src.expression.prepare import convertToPyExpr


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def calculate(expression: str) -> Optional[Union[int, float]]:
    if not isValidExpression(expression):
        return None

    if expression.strip():
        return eval(convertToPyExpr(expression))