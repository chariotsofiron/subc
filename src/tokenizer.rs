use crate::token::{Token, TokenType};

/// A tokenizer for the C language.
pub struct Tokenizer<'a> {
    pos: usize,
    text: &'a str,
}

impl<'a> Tokenizer<'a> {
    pub const fn new(text: &'a str) -> Self {
        Self { pos: 0, text }
    }

    /// Parses the next token from the text stream.
    fn next_token(&self) -> Option<Token> {
        let tokens = [
            // symbols
            (";", TokenType::Semicolon),
            (":", TokenType::Colon),
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
                return Some(Token {
                    token_type,
                    lexeme: lexeme.to_string(),
                    pos: self.pos,
                });
            }
        }

        // variable-length token
        let mut chars = self.text[self.pos..].chars().peekable();
        match chars.peek()? {
            ch if ch.is_ascii_digit() => Some(Token {
                token_type: TokenType::Number,
                lexeme: chars.take_while(char::is_ascii_digit).collect(),
                pos: self.pos,
            }),
            ch if ch.is_ascii_alphabetic() => Some(Token {
                token_type: TokenType::Identifier,
                lexeme: chars.take_while(char::is_ascii_alphanumeric).collect(),
                pos: self.pos,
            }),
            ch => panic!("Unexpected character: '{ch}'"),
        }
    }

    /// Consumes whitespace and comments
    fn consume_whitespace(&mut self) {
        let mut chars = self.text[self.pos..].chars();
        loop {
            match chars.next() {
                Some(ch) if ch.is_whitespace() => self.pos += ch.len_utf8(),
                Some('/') => match chars.next() {
                    Some('/') => {
                        self.pos += 2;
                        chars
                            .by_ref()
                            .take_while(|ch| *ch != '\n')
                            .for_each(|c| self.pos += c.len_utf8());
                    }
                    Some('*') => {
                        self.pos += 2;
                        while let Some(ch) = chars.next() {
                            if ch == '*' && chars.next() == Some('/') {
                                self.pos += 2;
                                break;
                            }
                            self.pos += ch.len_utf8();
                        }
                    }
                    Some(c) => {
                        self.pos += 1 + c.len_utf8();
                    }
                    None => {
                        self.pos += 1;
                        break;
                    }
                },
                _ => break,
            }
        }
    }
}

impl<'a> Iterator for Tokenizer<'a> {
    type Item = Token;

    fn next(&mut self) -> Option<Self::Item> {
        self.consume_whitespace();
        let tok = self.next_token();
        if let Some(ref tok) = tok {
            self.pos += tok.lexeme.len();
        }
        tok
    }
}
