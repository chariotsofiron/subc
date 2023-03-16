use crate::token::{Token, Type};

/// A tokenizer for the C language.
pub struct Tokenizer<'a> {
    pos: usize,
    text: &'a str,
}

impl<'a> Tokenizer<'a> {
    pub const fn new(text: &'a str) -> Self {
        Tokenizer { pos: 0, text }
    }

    fn get_token(&mut self) -> Token {
        let tokens = [
            // symbols
            (";", Type::Semicolon),
            ("(", Type::LParen),
            (")", Type::RParen),
            ("{", Type::LBrace),
            ("}", Type::RBrace),
            ("?", Type::Question),
            ("||", Type::LogOr),
            ("&&", Type::LogAnd),
            ("|", Type::BitOr),
            ("^", Type::BitXor),
            ("&", Type::BitAnd),
            ("==", Type::Equal),
            ("!=", Type::NotEqual),
            ("<", Type::Less),
            ("<=", Type::LessEqual),
            (">", Type::Greater),
            (">=", Type::GreaterEqual),
            ("<<", Type::ShiftLeft),
            (">>", Type::ShiftRight),
            ("+", Type::Plus),
            ("-", Type::Minus),
            ("*", Type::Star),
            ("/", Type::Slash),
            ("%", Type::Percent),
            ("++", Type::Increment),
            ("--", Type::Decrement),
            (".", Type::Point),
            ("->", Type::Arrow),
            ("[", Type::LSquare),
            ("]", Type::RSquare),
            (",", Type::Comma),
            ("=", Type::Assign),
            // keywords
            ("if", Type::If),
            ("else", Type::Else),
            ("for", Type::For),
            ("while", Type::While),
            ("return", Type::Return),
            ("int", Type::Int),
            ("char", Type::Char),
            ("void", Type::Void),
            ("struct", Type::Struct),
            ("enum", Type::Enum),
        ];

        // fixed-length token
        for (lexeme, token_type) in tokens {
            if self.text[self.pos..].starts_with(lexeme) {
                return Token {
                    type_: token_type,
                    lexeme: lexeme.to_owned(),
                    index: self.pos,
                };
            }
        }

        // variable-length token
        let mut chars = self.text[self.pos..].chars();
        let (token_type, end) = match chars.next().expect("Unexpected end of file") {
            ch if ch.is_ascii_digit() => {
                (Type::Number, chars.take_while(char::is_ascii_digit).count())
            }
            ch if ch.is_ascii_alphabetic() => (
                Type::Identifier,
                chars.take_while(char::is_ascii_alphanumeric).count(),
            ),
            ch => panic!("Unexpected character: '{ch}'"),
        };
        Token {
            type_: token_type,
            lexeme: self.text[self.pos..=(self.pos + end)].to_owned(),
            index: self.pos,
        }
    }

    /// Consumes whitespace and comments and returns whether there is more text to process.
    fn consume_whitespace(&mut self) -> bool {
        loop {
            if self.pos >= self.text.len() {
                return false;
            } else if self.text[self.pos..].starts_with("//") {
                // line comment
                self.pos += 2;
                for ch in self.text[self.pos..].chars() {
                    self.pos += ch.len_utf8();
                    if ch == '\n' {
                        break;
                    }
                }
            } else if self.text[self.pos..].starts_with("/*") {
                // block comment
                self.pos += 2;
                let mut chars = self.text[self.pos..].chars();
                while !self.text[self.pos..].starts_with("*/") {
                    self.pos += chars.next().unwrap().len_utf8();
                }
                self.pos += 2;
            } else if self.text[self.pos..] // whitespace
                .chars()
                .next()
                .map_or(false, char::is_whitespace)
            {
                self.pos += 1;
            } else {
                return true;
            }
        }
    }
}

impl<'a> Iterator for Tokenizer<'a> {
    type Item = Token;

    fn next(&mut self) -> Option<Self::Item> {
        if self.consume_whitespace() {
            let token = self.get_token();
            self.pos += token.lexeme.len();
            Some(token)
        } else {
            None
        }
    }
}
