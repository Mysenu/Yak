from typing import Tuple


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
