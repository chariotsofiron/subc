"""
run the compiler on a particular test case
"""
import sys

from subc.compiler import Compiler
from subc.tokenizer import tokenize
from subc.virtual_machine import execute


def main():
    """main method"""
    file_name = sys.argv[1]
    src = open(file_name).read()
    tokens = tokenize(src)
    pc_start, program, data_segment = Compiler(tokens).parse_global_declarations()
    execute(pc_start, program, data_segment)


if __name__ == "__main__":
    main()
