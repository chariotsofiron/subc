mod compiler;
mod opcode;
mod token;
mod tokenizer;
mod symbol_table;
mod ctype;
use crate::tokenizer::Tokenizer;

fn main() {
    let program = std::fs::read_to_string("examples/test2.c").unwrap();

    // let tokens = Tokenizer::new(&program).into_iter().peekable();
}
