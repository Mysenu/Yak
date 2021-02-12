from pathlib import Path
from typing import List

from PyQt5.QtCore import QStandardPaths

CACHE_DIR = Path(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))
CACHE_FILE = CACHE_DIR / 'history'


def saveHistoryToFile(expressions: List[str], file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(expressions))


def addExpressionToHistoryCache(expression: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        exit(1)

    if CACHE_FILE.exists() and (CACHE_FILE.stat().st_size > 0):
        with open(CACHE_FILE, 'a', encoding='utf-8') as file:
            file.write('\n' + expression)
    else:
        with open(CACHE_FILE, 'w', encoding='utf-8') as file:
            file.write(expression)


def loadHistoryFromCache() -> List[str]:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as file:
            expressions = file.read()
            return expressions.split('\n')
    else:
        return []


def clearHistoryCache() -> None:
    if CACHE_FILE.exists():
        open(CACHE_FILE, 'w', encoding='utf-8').close()
