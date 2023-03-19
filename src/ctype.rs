#[derive(Clone, Debug)]
pub enum CType {
    Int,
    Char,
    Void,
    Struct(usize),
    Pointer(Box<CType>),
}
