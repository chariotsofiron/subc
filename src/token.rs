#[derive(Debug, PartialEq, Clone, Copy, Eq)]
pub enum Type {
    // literals
    Identifier,
    Number,

    // symbols
    Semicolon,    // ;
    LParen,       // (
    RParen,       // )
    LBrace,       // {
    RBrace,       // }
    Question,     // ?
    LogOr,        // ||
    LogAnd,       // &&
    BitOr,        // |
    BitXor,       // ^
    BitAnd,       // &
    Equal,        // ==
    NotEqual,     // !=
    Less,         // <
    LessEqual,    // <=
    Greater,      // >
    GreaterEqual, // >=
    ShiftLeft,    // <<
    ShiftRight,   // >>
    Plus,         // +
    Minus,        // -
    Star,         // *
    Slash,        // /
    Percent,      // %
    Increment,    // ++
    Decrement,    // --
    Point,        // .
    Arrow,        // ->
    LSquare,      // [
    RSquare,      // ]
    Comma,        // ,
    Assign,       // =

    // keywords
    If,     // if
    Else,   // else
    For,    // for
    While,  // while
    Return, // return

    // types
    Int,    // int
    Char,   // char
    Void,   // void
    Struct, // struct
    Enum,   // enum
}

impl Type {
    pub const fn precedence(self) -> usize {
        match self {
            Self::Assign => 1,
            Self::Question => 2,
            Self::LogOr => 3,
            Self::LogAnd => 4,
            Self::BitOr => 5,
            Self::BitXor => 6,
            Self::BitAnd => 7,
            Self::Equal | Self::NotEqual => 8,
            Self::Less | Self::LessEqual | Self::Greater | Self::GreaterEqual => 9,
            Self::ShiftLeft | Self::ShiftRight => 10,
            Self::Plus | Self::Minus => 11,
            Self::Star | Self::Slash | Self::Percent => 12,
            Self::Increment | Self::Decrement | Self::Point | Self::Arrow | Self::LSquare => 13,
            _ => 0,
        }
    }

    pub const fn is_type(self) -> bool {
        matches!(
            self,
            Self::Int | Self::Char | Self::Void | Self::Struct | Self::Enum
        )
    }
}

#[derive(Debug, Clone)]
pub struct Token {
    pub type_: Type,
    pub lexeme: String,
    pub index: usize,
}
