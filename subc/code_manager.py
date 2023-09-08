"""the program module"""


class Program:
    """Represents an assembly program capable of being executed by the
    virtual machine"""

    def __init__(self):
        self.instructions = []
        self.label_ctr = 0

    def __repr__(self):
        asm = ""
        opcodes = (x for x in self.instructions)
        for opcode in opcodes:
            asm += opcode
            if opcode in {"LEA", "IMM", "JMP", "JSR", "BZ", "BNZ", "ENT", "ADJ"}:
                asm += f" {next(opcodes)}"
            asm += "\n"

        return asm

    def __len__(self):
        """get the length of the program in bytes"""
        return len(self.instructions)

    def __getitem__(self, index):
        """get the byte at `index` in the program"""
        return self.instructions[index]

    def __setitem__(self, index, item):
        """set the byte at `index` in the program"""
        self.instructions[index] = item

    def add(self, *args):
        """add the sequence of bytes to the program"""
        self.instructions.extend(args)
