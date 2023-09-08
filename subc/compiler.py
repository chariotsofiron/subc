import sys
from typing import Iterator, Optional

from subc.code_manager import Program
from subc.grammar import get_prec
from subc.scope_manager import RedeclaredError, SymbolTable, Types, UndeclaredError
from subc.tokenizer import Token

# identifier kinds
LOCAL, GLOBAL, MEMBER, FUNC, SYS, ENUM, *_ = range(10)


class Compiler:
    def __init__(self, tokens: Iterator[Token]) -> None:
        self.tokens = tokens
        self.curr_tk = next(self.tokens)
        self.curr_ty = Types.Int
        self.symbol_table = SymbolTable()
        self.program = Program()
        self.data_segment: list[int] = []

        # Declare system calls
        self.symbol_table.declare_id("malloc", Types.Void + Types.Ptr, "MALLOC", SYS)
        self.symbol_table.declare_id("free", Types.Void, "FREE", SYS)
        self.symbol_table.declare_id("printf", Types.Int, "PRINTF", SYS)
        self.symbol_table.declare_id("exit", Types.Int, "EXIT", SYS)

    def error(self, msg: str) -> None:
        """Raise error"""
        print(f"{self.curr_tk.line}:{self.curr_tk.col}, {msg}")
        sys.exit()

    def accept(self, token: str) -> Optional[str]:
        """if the current token == token, consume it and return lexeme"""
        lexeme = self.curr_tk.lexeme
        if self.curr_tk.type != token:
            return None
        self.curr_tk = next(self.tokens, None)
        return lexeme

    def expect(self, token: Token, msg=""):
        """expect a token type, throw error if not"""
        lexeme = self.curr_tk.lexeme
        if not self.accept(token):
            self.error(msg or f"expected {token}")
        return lexeme

    ###########################################################
    ## EXPRESSION PARSER
    ###########################################################

    def parse_expression(self, level: int = 0) -> None:
        # parse factor
        if self.curr_tk.type == "Num":
            self.program.add("IMM", self.expect("Num"))
            self.curr_ty = Types.Int

        elif self.curr_tk.type == "Str":
            self.program.add("IMM", len(self.data_segment))
            self.data_segment.extend(list(self.expect("Str")))
            self.data_segment.append(0)
            self.curr_ty = Types.Char + Types.Ptr

        elif self.curr_tk.type == "Id":
            ident = self.symbol_table.get_id(self.expect("Id"))

            if self.accept("("):  # parse function call
                if ident.kind not in (FUNC, SYS):
                    self.error("identifier is not a function")
                sz_params = 0
                while not self.accept(")"):
                    self.parse_expression()
                    self.program.add("PSH")
                    sz_params += self.symbol_table.sizeof(Types.Int)
                    if not self.curr_tk.type == ")":
                        self.expect(",")

                if ident.kind == FUNC:
                    self.program.add("JSR")
                self.program.add(ident.value)

                if sz_params:
                    self.program.add("ADJ", sz_params)

            elif ident.kind == ENUM:  # enum
                self.program.add("IMM", ident.value)
            else:
                if ident.kind == LOCAL:
                    self.program.add("LEA", ident.value)
                elif ident.kind == GLOBAL:
                    self.program.add("IMM", ident.value)
                else:
                    self.error("Not an identifier")
                if ident.type == Types.Char:
                    self.program.add("LC")
                if ident.type == Types.Int or ident.type >= Types.Ptr:
                    self.program.add("LI")
            self.curr_ty = ident.type

        elif self.accept("sizeof"):
            self.expect("(")
            sz_type = self.parse_base_type()
            while self.accept("*"):
                sz_type += Types.Ptr
            self.expect(")")
            self.program.add("IMM", self.symbol_table.sizeof(sz_type))

        elif self.accept("("):  # casting
            if self.curr_tk.type in ("void", "char", "int", "struct"):
                if self.accept("void"):
                    cast_type = Types.Void
                elif self.accept("char"):
                    cast_type = Types.Char
                elif self.accept("int"):
                    cast_type = Types.Int
                elif self.accept("struct"):
                    cast_type = self.symbol_table.get_tag(self.expect("Id"))
                while self.accept("*"):
                    cast_type += Types.Ptr
                self.expect(")")
                self.parse_expression(get_prec("++"))
                self.curr_ty = cast_type
            else:
                self.parse_expression()
                self.expect(")")

        elif self.accept("*"):  # dereference
            self.parse_expression(get_prec("++"))
            self.curr_ty -= Types.Ptr
            if self.curr_ty <= 0:
                self.error("bad dereference")
            self.program.add("LC" if self.curr_ty == Types.Char else "LI")

        elif self.accept("&"):  # address-of
            self.parse_expression(get_prec("++"))
            if self.program[-1] in ("LC", "LI"):
                self.program.instructions.pop()
            self.curr_ty += Types.Ptr

        elif self.curr_tk.type in ("++", "--"):  # pre-inc/dec
            op = self.curr_tk.type
            if not self.accept("++"):
                self.expect("--")
            self.parse_expression(get_prec("++"))
            if not self.program[-1] in ("LC", "LI"):
                self.error("bad lvalue in pre-increment")
            sz = self.symbol_table.get_add_size(self.curr_ty)
            self.program.add(
                "PSH",
                "IMM",
                sz,
                "ADD" if op == "++" else "SUB",
                "SC" if self.curr_ty == Types.Char else "SI",
            )

        elif self.accept("!"):  # not
            self.parse_expression(get_prec("++"))
            self.program.add("PSH", "IMM", 0, "EQL")
            self.curr_ty = Types.Int

        elif self.accept("~"):  # invert
            self.parse_expression(get_prec("++"))
            self.program.add("PSH", "IMM", -1, "XOR")
            self.curr_ty = Types.Int

        elif self.accept("+"):  # unary plus
            self.parse_expression(get_prec("++"))
            self.curr_ty = Types.Int

        elif self.accept("-"):  # unary minus
            self.program.add("IMM")
            if self.curr_tk.type == "Num":
                self.program.add(-int(self.expect("Num")))
            else:
                self.program.add(-1, "PSH")
                self.parse_expression(get_prec("++"))
                self.program.add("MUL")

        else:
            self.error("bad expression")

        while get_prec(self.curr_tk.type) >= level:
            temp_type = self.curr_ty

            if self.accept("="):  # assignment
                if self.program[-1] in ("LI", "LC"):
                    self.program[-1] = "PSH"
                else:
                    self.error("bad lvalue in assignment")
                self.parse_expression()
                self.curr_ty = temp_type  # assign-expr is type of lvalue
                self.program.add("SC" if self.curr_ty == Types.Char else "SI")

            elif self.accept("?"):  # ternary
                self.program.add("BZ", 0)
                b = len(self.program) - 1
                self.parse_expression()
                self.program.add("JMP", 0)
                self.program[b] = len(self.program)
                b = len(self.program) - 1
                self.expect(":")
                self.parse_expression(get_prec("?"))
                self.program[b] = len(self.program)

            elif self.accept("||"):
                self.program.add("BNZ", 0)
                b = len(self.program) - 1
                self.parse_expression(get_prec("&&"))
                self.program[b] = len(self.program)
                self.curr_ty = Types.Int

            elif self.accept("&&"):
                self.program.add("BZ", 0)
                b = len(self.program) - 1
                self.parse_expression(get_prec("|"))
                self.program[b] = len(self.program)
                self.curr_ty = Types.Int

            elif self.accept("+"):
                self.program.add("PSH")
                self.parse_expression(get_prec("*"))
                sz = self.symbol_table.get_add_size(temp_type)
                if sz > 1:
                    self.program.add("PSH", "IMM", sz, "MUL")
                self.program.add("ADD")
                self.curr_ty = temp_type

            elif self.accept("-"):
                self.program.add("PSH")
                self.parse_expression(get_prec("*"))
                sz = self.symbol_table.get_add_size(temp_type)
                if sz > 1:
                    if self.curr_ty == temp_type:
                        self.program.add("SUB", "PSH", "IMM", sz, "DIV")
                        self.curr_ty = Types.Int
                    else:
                        self.program.add("PSH", "IMM", sz, "MUL", "SUB")
                else:
                    self.program.add("SUB")
                self.curr_ty = temp_type

            elif self.curr_tk.type in ("++", "--"):  # post increment
                if not self.program[-1] in ("LC", "LI"):
                    self.error("bad lvalue in post increment")
                self.program.instructions.insert(-1, "PSH")
                sz = self.symbol_table.get_add_size(self.curr_ty)
                self.program.add(
                    "PSH",
                    "IMM",
                    sz,
                    "ADD" if self.curr_tk.type == "++" else "SUB",
                    "SC" if self.curr_ty == Types.Char else "SI",
                    "PSH",
                    "IMM",
                    sz,
                    "SUB" if self.curr_tk.type == "++" else "ADD",
                )
                if not self.accept("++"):
                    self.expect("--")

            elif self.curr_tk.type in (".", "->"):
                if self.accept("."):
                    self.curr_ty += Types.Ptr
                else:
                    self.expect("->")
                name = self.expect("Id")
                member = self.symbol_table.get_member(self.curr_ty - Types.Ptr, name)
                if member.offset:
                    self.program.add("PSH", "IMM", member.offset, "ADD")
                self.curr_ty = member.type
                self.program.add("LC" if self.curr_ty == Types.Char else "LI")

            elif self.accept("["):
                self.program.add("PSH")
                self.parse_expression()
                self.expect("]")
                if temp_type < Types.Ptr:
                    self.error("subscripted value is neither array nor pointer")
                temp_type -= Types.Ptr
                sz = self.symbol_table.sizeof(temp_type)
                if sz > 1:
                    self.program.add("PSH", "IMM", sz, "MUL")
                self.program.add("ADD")
                self.curr_ty = temp_type
                if self.curr_ty <= Types.Int or self.curr_ty >= Types.Ptr:
                    self.program.add("LC" if self.curr_ty == Types.Char else "LI")

            else:
                for op, prec in (
                    ("|", "IOR"),
                    ("^", "XOR"),
                    ("&", "AND"),
                    ("==", "EQL"),
                    ("!=", "NEQ"),
                    (">", "GTR"),
                    ("<", "LSS"),
                    (">=", "GEQ"),
                    ("<=", "LEQ"),
                    ("<<", "SHL"),
                    (">>", "SHR"),
                    ("*", "MUL"),
                    ("/", "DIV"),
                    ("%", "MOD"),
                ):
                    if self.accept(op):
                        self.program.add("PSH")
                        self.parse_expression(get_prec(prec) + 1)
                        self.program.add(prec)
                        self.curr_ty = Types.Int
                        break
                else:
                    self.error("error parsing expression")

    ###########################################################
    ## STATEMENT PARSING
    ###########################################################
    def parse_statement(self, offset: int) -> None:
        if self.accept(";"):  # empty statement
            pass

        elif self.curr_tk.type in ("void", "char", "int", "struct", "enum"):
            offset = self.parse_declaration(LOCAL, offset)

        elif self.accept("if"):  # if statement
            self.expect("(")
            self.parse_expression()
            self.expect(")")
            self.program.add("BZ", 0)
            b = len(self.program) - 1
            offset = self.parse_statement(offset)
            if self.accept("else"):
                self.program.add("JMP", 0)
                self.program[b] = len(self.program)
                b = len(self.program) - 1
                offset = self.parse_statement(offset)
            self.program[b] = len(self.program)

        elif self.accept("while"):
            a = len(self.program)
            self.expect("(")
            self.parse_expression()
            self.expect(")")
            self.program.add("BZ", 0)
            b = len(self.program) - 1
            offset = self.parse_statement(offset)
            self.program.add("JMP", a)
            self.program[b] = len(self.program)

        elif self.accept("return"):
            self.parse_expression()
            self.program.add("RET")
            self.expect(";")

        elif self.accept("{"):
            while not self.accept("}"):
                offset = self.parse_statement(offset)

        else:
            self.parse_expression()
            self.expect(";")
        return offset

    ##########################################################################
    ## DECLARATION PARSING
    ##########################################################################

    def parse_base_type(self):
        """parse base type"""
        if self.accept("void"):
            return Types.Void

        if self.accept("char"):
            return Types.Char

        if self.accept("int"):
            return Types.Int

        if self.accept("enum"):
            name = self.accept("Id")  # optional
            if self.accept("{"):
                self.symbol_table.declare_tag(name)
                i = 0
                while not self.accept("}"):
                    name = self.expect("Id")
                    if self.accept("="):
                        i = int(self.expect("Num"))
                    self.symbol_table.declare_id(name, Types.Int, i, ENUM)
                    if not self.curr_tk.type == "}":
                        self.expect(",", "expected , or }")
                    i += 1
            return Types.Int

        if self.accept("struct"):
            name = self.accept("Id")  # optional
            if self.accept("{"):
                tag_type = self.symbol_table.next_type()
                if name:
                    self.symbol_table.declare_tag(name, tag_type)
                offset = 0
                while not self.accept("}"):
                    offset = self.parse_declaration(MEMBER, offset, tag_type)
                self.symbol_table.update_size(tag_type, offset)
                return tag_type
            return self.symbol_table.get_tag(name)

        self.error("expected type")

    def parse_declaration(self, kind: int, offset: int, tag_type=None) -> int:
        """parse a declaration"""
        base_type = self.parse_base_type()
        while not self.accept(";"):
            ty = base_type

            while self.accept("*"):  # parse pointers
                ty += Types.Ptr

            name = self.expect("Id")

            if kind == GLOBAL and self.accept("("):  # parse function declaration
                self.symbol_table.declare_id(name, ty, len(self.program), FUNC)
                self.symbol_table.create_scope()

                i = 0
                while not self.accept(")"):  # parse parameter declarations
                    i = self.parse_declaration(FUNC, i)
                self.symbol_table.fix_params(i)

                self.expect("{")
                i = 4
                while not self.accept("}"):  # parse function body
                    i = self.parse_statement(i)

                self.program.add("RET")
                self.symbol_table.destroy_scope()
                return offset

            if self.symbol_table.sizeof(ty) == 0:
                self.error("incomplete type")

            offset = self.symbol_table.align(offset, ty)

            if kind == MEMBER:  # parse struct or union member declaration
                self.symbol_table.update_alignment(tag_type, ty)
                self.symbol_table.declare_member(tag_type, name, ty, offset)

            elif kind == LOCAL:
                self.symbol_table.declare_id(name, ty, -offset, LOCAL)
                self.program.add("ADJ", -self.symbol_table.sizeof(ty))

            else:  # normal variable declaration
                self.symbol_table.declare_id(
                    name, ty, offset, kind if kind != FUNC else LOCAL
                )

            if self.accept("="):  # assignment declaration
                address = self.symbol_table.get_id(name).value
                self.program.add("LEA" if kind == LOCAL else "IMM", address, "PSH")
                self.parse_expression()
                self.program.add("SC" if ty == Types.Char else "SI")

            offset += self.symbol_table.sizeof(ty)

            if kind == FUNC:  # function parameters should be aligned to int
                offset = self.symbol_table.align(offset, Types.Int)
                if self.curr_tk.type != ")":
                    self.expect(",", "expected , or )")
                return offset

            if self.curr_tk.type != ";":
                self.expect(",", "expected , or ;")

        return offset

    def parse_global_declarations(self) -> None:
        """parse global declarations"""
        offset = len(self.data_segment)
        while self.curr_tk:
            try:
                offset = self.parse_declaration(GLOBAL, offset)
            except UndeclaredError:
                self.error("identifier not declared")
            except RedeclaredError:
                self.error("identifier already declared")

        pc_start = self.symbol_table.get_id("main").value
        return pc_start, self.program.instructions, self.data_segment
