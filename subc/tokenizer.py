import collections
import re
import sys
from typing import Iterator, Optional

from subc import grammar

Token = collections.namedtuple("Token", ["type", "lexeme", "line", "col"])


def tokenize(source: str) -> Iterator[Token]:
    """Tokenize the source code."""
    i = 0
    line = col = 1

    def accept(pattern: str) -> Optional[str]:
        nonlocal i, line, col
        if match := re.match(pattern, source[i:]):
            text = match.group()
            i += len(text)
            line += text.count("\n")
            col = len(text.splitlines()[-1])
            return text
        return None

    while i < len(source):
        if accept(r"\s+|\/\*(.|\n)*?\*\/|\/\/.*"):  # whitespace and comments
            continue

        for token in grammar.TOKEN_TYPES:
            if accept(re.escape(token)):
                yield Token(token, token, line, col)
                break
        else:
            if match := accept(r"\".*\""):  # strings
                yield Token("Str", match[1:-1], line, col)
            elif match := accept(r"\'\w\'"):  # chars
                yield Token("Num", match[1:-1], line, col)
            elif match := accept(r"[_a-zA-Z][_a-zA-Z0-9]*"):  # identifiers
                yield Token("Id", match, line, col)
            elif match := accept(r"\d+"):  # numbers
                yield Token("Num", match, line, col)
            else:
                print(source[i : source.index(" ", i)])
                sys.exit()
