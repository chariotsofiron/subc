use std::collections::HashMap;

use crate::ctype::CType;

#[derive(Clone, Copy, Debug)]
pub enum Scope {
    Local,
    Global,
    Member,
    Function,
    System,
    Enum,
}

#[derive(Clone, Debug)]
pub struct Symbol(pub CType, pub Scope);

#[derive(Default)]
pub struct SymbolTable {
    levels: Vec<HashMap<String, Symbol>>,
}

impl SymbolTable {
    pub fn create_scope(&mut self) {
        self.levels.push(HashMap::new());
    }

    pub fn destroy_scope(&mut self) {
        self.levels.pop();
    }

    pub fn insert(&mut self, name: &str, symbol: Symbol) {
        println!(
            "new symbol: {name} {symbol:?} into level {:?}",
            self.levels.len() - 1
        );
        self.levels
            .last_mut()
            .unwrap()
            .insert(name.to_string(), symbol);
    }

    /// Returns the last Value this type was assigned to
    pub fn lookup(&self, name: &str) -> Option<Symbol> {
        for level in self.levels.iter().rev() {
            if let Some(symbol) = level.get(name) {
                return Some(symbol.clone());
            }
        }
        None
    }
}
