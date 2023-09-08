import enum

from subc.scope_manager import Sizes


class Opcode(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()
    EQ = enum.auto()
    NE = enum.auto()
    LT = enum.auto()
    GT = enum.auto()
    LE = enum.auto()
    GE = enum.auto()
    SHL = enum.auto()
    SHR = enum.auto()
    AND = enum.auto()
    OR = enum.auto()
    XOR = enum.auto()
    NOT = enum.auto()
    NEG = enum.auto()
    PSH = enum.auto()
    POP = enum.auto()
    LEA = enum.auto()
    IMM = enum.auto()
    JMP = enum.auto()
    JSR = enum.auto()
    BZ = enum.auto()
    BNZ = enum.auto()
    ADJ = enum.auto()


def execute(pc_start: int, program: list, data_segment) -> int:
    """Runs the program and returns the exit code."""
    program.extend(("PSH", "EXIT"))  # EXIT for main return
    memory = [0] * 2048
    memory[: len(data_segment)] = data_segment
    heap = len(data_segment)

    # initialize processor registers
    pc = pc_start
    sp = (len(memory) - 1) & -Sizes.Int  # round down towards multiple of Int size
    bp = 0
    ax = 0

    memory[sp] = len(program) - 2  # return address
    sp -= Sizes.Int
    memory[sp] = bp  # base pointer
    bp = sp

    cycle = 0
    while True:
        cycle += 1
        opcode = program[pc]
        pc += 1

        # z = {"LEA", "IMM", "JMP", "JSR", "BZ", "BNZ", "ADJ"}
        # print(
        #     "{:3d}: {:4s} {:3s} ".format(
        #         cycle, opcode, str(program[pc]) if opcode in z else ""
        #     ),
        #     end="",
        # )
        # print("ax: {:4} bp: {:4} sp: {:4}  ".format(ax, bp, sp), end="")
        # for x in memory[-48::4]:
        #     print(f"{x:4},", end=" ")
        # print()

        if opcode == "LEA":
            ax = bp + int(program[pc])
            pc += 1
        elif opcode == "IMM":
            ax = int(program[pc])
            pc += 1
        elif opcode == "JMP":
            pc = int(program[pc])
        elif opcode == "JSR":
            sp -= Sizes.Int
            memory[sp] = pc + 1
            sp -= Sizes.Int
            memory[sp] = bp
            bp = sp
            pc = int(program[pc])
        elif opcode == "BZ":
            if not ax:
                pc = int(program[pc])
            else:
                pc += 1
        elif opcode == "BNZ":
            if ax:
                pc = int(program[pc])
            else:
                pc += 1
        elif opcode == "ADJ":
            sp += int(program[pc])
            pc += 1
        elif opcode == "RET":
            sp = bp
            bp = memory[sp]
            sp += Sizes.Int
            pc = memory[sp]
            sp += Sizes.Int
        elif opcode == "LI":
            ax = memory[ax]
        elif opcode == "LC":
            ax = memory[ax]
        elif opcode == "SI":
            memory[memory[sp]] = ax
            sp += Sizes.Int
        elif opcode == "SC":
            memory[memory[sp]] = ax
            sp += Sizes.Int
        elif opcode == "PSH":
            sp -= Sizes.Int
            memory[sp] = ax

        elif opcode == "IOR":
            ax = memory[sp] | ax
            sp += Sizes.Int
        elif opcode == "XOR":
            ax = memory[sp] ^ ax
            sp += Sizes.Int
        elif opcode == "AND":
            ax = memory[sp] & ax
            sp += Sizes.Int
        elif opcode == "EQL":
            ax = int(memory[sp] == ax)
            sp += Sizes.Int
        elif opcode == "NEQ":
            ax = int(memory[sp] != ax)
            sp += Sizes.Int
        elif opcode == "LSS":
            ax = int(memory[sp] < ax)
            sp += Sizes.Int
        elif opcode == "GTR":
            ax = int(memory[sp] > ax)
            sp += Sizes.Int
        elif opcode == "LEQ":
            ax = int(memory[sp] <= ax)
            sp += Sizes.Int
        elif opcode == "GEQ":
            ax = int(memory[sp] >= ax)
            sp += Sizes.Int
        elif opcode == "SHL":
            ax = memory[sp] << ax
            sp += Sizes.Int
        elif opcode == "SHR":
            ax = memory[sp] >> ax
            sp += Sizes.Int

        elif opcode == "ADD":
            ax = memory[sp] + ax
            sp += Sizes.Int
        elif opcode == "SUB":
            ax = memory[sp] - ax
            sp += Sizes.Int
        elif opcode == "MUL":
            ax = memory[sp] * ax
            sp += Sizes.Int
        elif opcode == "DIV":
            ax = memory[sp] // ax
            sp += Sizes.Int
        elif opcode == "MOD":
            ax = memory[sp] % ax
            sp += Sizes.Int

        elif opcode == "PRINTF":
            start = sp - Sizes.Int + program[pc + 1]
            string = "".join(memory[memory[start] : memory.index(0, memory[start])])
            string = string.replace("\\n", "\n")
            args = tuple(memory[start - Sizes.Int : sp - Sizes.Int : -Sizes.Int])
            print(string % args, end="")

        elif opcode == "MALLOC":
            args = memory[sp : sp + program[pc + 1]]
            ax = heap
            heap += args[0]

        elif opcode == "EXIT":
            print(f"exit({memory[sp]})")
            return memory[sp]

        else:
            print("unrecognized opcode")
            print(opcode)
            exit()
