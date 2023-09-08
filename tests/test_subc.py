from subc.compiler import Compiler
from subc.tokenizer import tokenize
from subc.virtual_machine import execute


def test():
    text = open("examples/fib.c").read()

    tokens = tokenize(text)
    pc_start, program, data_segment = Compiler(tokens).parse_global_declarations()
    assert execute(pc_start, program, data_segment) == 0
