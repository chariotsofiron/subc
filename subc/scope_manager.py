import collections
import enum
from typing import Optional


class Sizes(enum.IntEnum):
    Void = 0
    Char = 1
    Int = 4


class Types(enum.IntEnum):
    Void = 0
    Char = 1
    Int = 2
    Ptr = 256


class Identifier:
    def __init__(self, id_type, value, kind) -> None:
        self.type = id_type
        self.value = value
        self.kind = kind

    def __repr__(self) -> str:
        kind = ["local", "global", "member", "func", "sys", "enum"][self.kind]
        return f"{self.type:4}, {self.value:4}, {kind}"


Member = collections.namedtuple("Member", ["type", "offset"])


class UndeclaredError(Exception):
    """Undeclared."""


class RedeclaredError(Exception):
    """Redeclared."""


class SymbolTable:
    """the scope is represented by a stack of dicts"""

    ScopeLevel = collections.namedtuple("ScopeLevel", "identifiers tags")

    def __init__(self) -> None:
        self.levels: list[self.ScopeLevel] = [self.ScopeLevel({}, {})]
        self.members = {}  # indexed by members[struct_type][member_name]
        self.sizes = [Sizes.Void, Sizes.Char, Sizes.Int]
        self.alignments = [Sizes.Void, Sizes.Char, Sizes.Int]

    def __repr__(self) -> str:
        result = ""

        for level in reversed(self.levels[-1:]):
            result += "====================\n"
            result += "identifiers\n"
            result += "\n".join(
                f"{name:6}: {x}" for name, x in level.identifiers.items()
            )
            result += "\ntags\n"
            result += "\n".join(
                f"{name}: {tag_type}" for name, tag_type in level.tags.items()
            )
            result += "\n"
        result += "====================\n"
        result += f"sizes: {self.sizes}\nalign: {self.alignments}\n"

        return result

    def create_scope(self) -> None:
        """adds an additional scope level"""
        self.levels.append(self.ScopeLevel({}, {}))

    def destroy_scope(self) -> None:
        """destroys a scope level"""
        self.levels.pop()

    def declare_id(self, name: str, id_ty, offset: Optional[int] = None, kind=None):
        """declare an identifier"""
        if name in self.levels[-1].identifiers:
            raise RedeclaredError()
        new_id = Identifier(id_ty, offset, kind)
        self.levels[-1].identifiers[name] = new_id

    def declare_tag(self, name, tag_type=None):
        """declare tag for struct, union, enumerations"""
        if name:
            if name in self.levels[-1].identifiers:
                raise RedeclaredError()
            self.levels[-1].tags[name] = tag_type

        if tag_type:  # struct, union
            self.members[tag_type] = {}
            self.sizes.append(0)
            self.alignments.append(0)

    def declare_member(self, tag_type, name, ty, offset):
        if name in self.members[tag_type]:
            exit("duplicate member")
        self.members[tag_type][name] = Member(ty, offset)

    def get_id(self, name):
        for scope in reversed(self.levels):
            if name in scope.identifiers:
                return scope.identifiers[name]
        raise UndeclaredError()

    def get_tag(self, name: str):
        for scope in reversed(self.levels):
            if name in scope.tags:
                return scope.tags[name]
        raise UndeclaredError()

    def get_member(self, tag_type, name):
        return self.members[tag_type][name]

    def update_size(self, tag_type, offset):
        self.sizes[tag_type] = self.align(offset, tag_type)

    def update_alignment(self, tag_type, var_type):
        self.alignments[tag_type] = max(
            self.sizeof(var_type), self.alignments[tag_type]
        )

    def next_type(self):
        return len(self.sizes)

    def fix_params(self, sz_params):
        """parameters are pushed onto stack in reverse order so we need to
        fix their address"""

        for param in self.levels[-1].identifiers.values():
            if param.kind == 0:  # TODO should be local
                param.value = sz_params + self.sizeof(Types.Int) - param.value

    def sizeof(self, var_type) -> int:
        if var_type >= Types.Ptr:
            return self.sizes[Types.Int]
        return self.sizes[var_type]

    def get_add_size(self, var_type: Types) -> int:
        """Gets the size of the variable to add to the address."""
        if var_type >= Types.Ptr:
            return self.sizeof(var_type - Types.Ptr)
        return 1

    def get_align(self, var_type):
        if var_type >= Types.Ptr:
            return self.alignments[Types.Int]
        return self.alignments[var_type]

    def align(self, address, var_type):
        """align the address to the alignment of the var_type i.e. round up
        to nearest power of 2"""
        alignment = self.get_align(var_type)
        return (address + alignment - 1) & -alignment
