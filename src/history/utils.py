from typing import List, Optional
from pathlib import Path

from PyQt5.QtCore import QStandardPaths


CACHE_DIR = Path(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))
HISTORY_CACHE_FILE_NAME = 'calc'


def saveHistoryToFile(expressions: List[str], file_path: str) -> None:
    with open(file_path, 'w') as file:
        file.write('\n'.join(expressions))


def saveHistoryToCacheFile(expression: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        exit(1)

    file_path = CACHE_DIR / HISTORY_CACHE_FILE_NAME

    if file_path.exists() and (file_path.stat().st_size > 0):
        with open(file_path, 'a') as file:
            file.write('\n' + expression)
    else:
        with open(file_path, 'w') as file:
            file.write(expression)


def readHistoryCacheFile() -> Optional[List[str]]:
    file_path = CACHE_DIR / HISTORY_CACHE_FILE_NAME

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        exit(1)

    if file_path.exists():
        with open(file_path, 'r') as file:
            expressions = file.read()
    else:
        return

    return expressions.split('\n')


def clearHistoryCacheFile() -> None:
    open(CACHE_DIR / HISTORY_CACHE_FILE_NAME, 'w').close()
