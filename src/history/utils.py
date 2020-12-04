from typing import List


def saveHistoryToFile(expressions: List[str], file_path: str) -> None:
    with open(file_path, 'w') as file:
        file.write('\n'.join(expressions))
