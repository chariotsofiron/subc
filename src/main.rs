mod compiler;
mod ctype;
mod opcode;
mod symbol_table;
mod token;
mod tokenizer;
use crate::tokenizer::Tokenizer;

fn main() {
    let program = std::fs::read_to_string("examples/comments.c").unwrap();

    for token in Tokenizer::new(&program) {
        println!("{token:?}");
    }

    // let tokens = Tokenizer::new(&program).into_iter().peekable();
}
