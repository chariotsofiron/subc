use crate::tokenizer::Tokenizer;

mod tokenizer;
mod token;
fn main() {
    let program = std::fs::read_to_string("examples/test2.c").unwrap();

    for token in  Tokenizer::new(&program) {
        println!("{:?}", token);
    }
}
