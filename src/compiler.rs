use std::iter::Peekable;

use crate::ctype::CType;
use crate::token::{self, Token};
use crate::{opcode::Opcode, symbol_table::SymbolTable, token::TokenType, tokenizer::Tokenizer};

pub enum DecType {
    Global,
    Local,
    Parameter,
}

fn error(token: Option<Token>, msg: &str) -> ! {
    panic!("{token:?}: {msg}")
}

pub struct Compiler<'a> {
    tokens: Peekable<Tokenizer<'a>>,
    program: Vec<Opcode>,
    symbol_table: SymbolTable,
}

impl<'a> Compiler<'a> {
    pub fn new(tokens: Peekable<Tokenizer<'a>>) -> Self {
        Self {
            tokens,
            program: Vec::new(),
            symbol_table: SymbolTable::default(),
        }
    }

    /// Returns the lexeme of the next token if it matches the type
    fn accept(&mut self, token: TokenType) -> Option<String> {
        match self.tokens.peek() {
            Some(tok) if tok.token_type == token => self.tokens.next().map(|x| x.lexeme),
            _ => None,
        }
    }

    /// Returns the next token if it matches the given token, otherwise panics.
    fn expect(&mut self, token: TokenType) -> String {
        match self.accept(token) {
            Some(lexeme) => lexeme,
            None => error(
                self.tokens.peek().cloned(),
                &format!("expected token {token:?}"),
            ),
        }
    }

    fn walk_expression(&mut self) {}

    fn walk_statement(&mut self) {}

    fn parse_base_type(&mut self) -> CType {
        let token = self.tokens.next();
        match token.clone().map(|x| x.token_type) {
            Some(TokenType::Int) => CType::Int,
            Some(TokenType::Char) => CType::Char,
            Some(TokenType::Void) => CType::Void,
            Some(TokenType::Enum) => CType::Int,
            _ => error(token, "expected type keyword"),
        }
    }

    fn walk_declaration(&mut self, dectype: DecType) {}

    fn walk_global_declarations(&mut self) {
        while self.tokens.peek().is_some() {
            self.walk_declaration(DecType::Global);
        }
    }
}
