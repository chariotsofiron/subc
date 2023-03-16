use crate::{opcode::Opcode, symbol_table::SymbolTable, token::Token, tokenizer::Tokenizer};
use crate::token;

pub enum DecType {
    Global,
    Local,
    Parameter,
}

pub struct Compiler {
    tokens: Vec<Token>,
    program: Vec<Opcode>,
    symbol_table: SymbolTable,
}

impl Compiler {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self {
            tokens,
            program: Vec::new(),
            symbol_table: SymbolTable::default(),
        }
    }

    fn walk_expression(&mut self) {}

    fn walk_statement(&mut self) {}


    fn parse_base_type(&mut self) {
        match self.tokens.next() {
            Some(Token::Int) => {}
            Some(Token::Char) => {}
            Some(Token::Void) => {}
            _ => {}
        }
    }

    fn walk_declaration(&mut self, dectype: ) {
        
    }

    fn walk_global_declarations(&mut self) {
        while self.tokens.peek().is_some() {
            self.walk_declaration(DecType::Global);
        }
    }
}
