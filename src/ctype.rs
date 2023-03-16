#[derive(Clone, Debug)]
pub enum CType {
    Int,
    Char,
    Void,
    Pointer(Box<CType>),
}

impl CType {
    pub const fn size(&self) -> usize {
        match self {
            Self::Int => 4,
            Self::Char => 1,
            Self::Void => 0,
            Self::Pointer(_) => 8,
        }
    }
}
