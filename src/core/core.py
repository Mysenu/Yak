from src.expression.expressions import convertToPyExpr


def saveHistoryToFile(expressions: list, file_path: str) -> None:
    with open(file_path, 'w') as file:
        file.write('\n'.join(expressions))
