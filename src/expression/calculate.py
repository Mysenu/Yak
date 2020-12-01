from math import sqrt, pow
from typing import Union, Optional

from src.expression.check import isValidExpression
from src.expression.prepare import convertToPyExpr

pow = pow
sqrt = sqrt


def toPercent(value: Union[int, float]) -> float:
    return value * 0.01


def calculateExpr(expression: str) -> Optional[Union[int, float]]:
    if not isValidExpression(expression):
        return None

    if expression.strip():
        return eval(convertToPyExpr(expression))
