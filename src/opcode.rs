use crate::ctype::CType;

#[derive(Debug, Clone, Copy)]
pub enum Opcode {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Eq,
    Ne,
    Lt,
    Le,
    Gt,
    Ge,
    Jsr(usize, usize), // address, param + local size
    Bnz(usize),
    Ret(usize),
}

fn execute(program: &[Opcode]) {
    let mut memory = [0; 1024];
    let mut stack_pointer = memory.len();
    let mut ax: i32 = 0;
    let mut pc: usize = 0;

    loop {
        let opcode = program[pc];
        pc += 1;
        match opcode {
            Opcode::Add => {
                ax += memory[stack_pointer];
                stack_pointer += 4;
            }
            Opcode::Bnz(address) => {
                if ax != 0 {
                    pc = address;
                }
            }
            _ => {}
        }
    }
}
