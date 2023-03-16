use crate::token::{Token, TokenType};

/// A tokenizer for the C language.
pub struct Tokenizer<'a> {
    pos: usize,
    text: &'a str,
}

impl<'a> Tokenizer<'a> {
    pub fn new(text: &'a str) -> Self {
        Tokenizer { pos: 0, text }
    }

    fn get_token(&mut self) -> Token {
        let tokens = [
            // symbols
            (";", TokenType::Semicolon),
            ("(", TokenType::LParen),
            (")", TokenType::RParen),
            ("{", TokenType::LBrace),
            ("}", TokenType::RBrace),
            ("?", TokenType::Question),
            ("||", TokenType::LogOr),
            ("&&", TokenType::LogAnd),
            ("|", TokenType::BitOr),
            ("^", TokenType::BitXor),
            ("&", TokenType::BitAnd),
            ("==", TokenType::Equal),
            ("!=", TokenType::NotEqual),
            ("<", TokenType::Less),
            ("<=", TokenType::LessEqual),
            (">", TokenType::Greater),
            (">=", TokenType::GreaterEqual),
            ("<<", TokenType::ShiftLeft),
            (">>", TokenType::ShiftRight),
            ("+", TokenType::Plus),
            ("-", TokenType::Minus),
            ("*", TokenType::Star),
            ("/", TokenType::Slash),
            ("%", TokenType::Percent),
            ("++", TokenType::Increment),
            ("--", TokenType::Decrement),
            (".", TokenType::Point),
            ("->", TokenType::Arrow),
            ("[", TokenType::LSquare),
            ("]", TokenType::RSquare),
            (",", TokenType::Comma),
            ("=", TokenType::Assign),
            // keywords
            ("if", TokenType::If),
            ("else", TokenType::Else),
            ("for", TokenType::For),
            ("while", TokenType::While),
            ("return", TokenType::Return),
            ("int", TokenType::Int),
            ("char", TokenType::Char),
            ("void", TokenType::Void),
            ("struct", TokenType::Struct),
            ("enum", TokenType::Enum),
        ];

        // fixed-length token
        for (lexeme, token_type) in tokens {
            if self.text[self.pos..].starts_with(lexeme) {
                return Token {
                    token_type,
                    lexeme: lexeme.to_owned(),
                    index: self.pos,
                };
            }
        }

        // variable-length token
        let mut chars = self.text[self.pos..].chars();
        let (token_type, end) = match chars.next().expect("Unexpected end of file") {
            ch if ch.is_ascii_digit() => (
                TokenType::Number,
                chars.take_while(char::is_ascii_digit).count(),
            ),
            ch if ch.is_ascii_alphabetic() => (
                TokenType::Identifier,
                chars.take_while(char::is_ascii_alphanumeric).count(),
            ),
            ch => panic!("Unexpected character: '{ch}'"),
        };
        Token {
            token_type,
            lexeme: self.text[self.pos..self.pos + end + 1].to_owned(),
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
                let mut chars = self.text[self.pos..].chars();
                while let Some(ch) = chars.next() {
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
                .map_or(false, |c| c.is_whitespace())
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
