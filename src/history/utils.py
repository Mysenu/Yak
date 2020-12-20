from typing import List, Optional

from PyQt5.QtCore import QStandardPaths
from pathlib import Path


CACHE_DIR = Path(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))


def saveHistoryToFile(expressions: List[str], file_path: str) -> None:
    with open(file_path, 'w') as file:
        file.write('\n'.join(expressions))


def saveHistoryToCacheFile(expression: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        exit(2)

    file_path = CACHE_DIR / 'calc'

    if file_path.exists():
        with open(file_path, 'a') as file:
            file.write('\n' + expression)
    else:
        with open(file_path, 'w') as file:
            file.write(expression)


def readHistoryCacheFile() -> Optional[List[str]]:

    file_path = CACHE_DIR / 'calc'

    if file_path.exists():
        with open(file_path, 'r') as file:
            expressions = file.read()
    else:
        return

    return expressions.split('\n')
