"""different types of tokens that can be parsed"""
TOKEN_TYPES = (
    # keywords
    "void",
    "int",
    "float",
    "char",
    "enum",
    "struct",
    "union",
    "if",
    "else",
    "for",
    "while",
    "return",
    "sizeof",
    # operators
    "&&",
    "||",
    "->",
    "++",
    "--",
    "==",
    "!=",
    ">=",
    "<=",
    ">",
    "<",
    "+",
    "-",
    "*",
    "&",
    "/",
    "%",
    "!",
    "=",
    "~",
    "?",
    "[",
    # punctuation
    "(",
    ")",
    "]",
    "{",
    "}",
    ";",
    ",",
    ":",
    ";",
    ".",
)

PREC = (
    {"="},
    {"?"},
    {"||"},
    {"&&"},
    {"|"},
    {"^"},
    {"&"},
    {"==", "!="},
    {"<", "<=", ">", ">="},
    {"<<", ">>"},
    {"+", "-"},
    {"*", "/", "%"},
    {"++", "--", ".", "->", "["},
)


def get_prec(operator: str) -> int:
    """get the precedence of an operator"""
    for i, level in enumerate(PREC):
        if operator in level:
            return i
    return -1
