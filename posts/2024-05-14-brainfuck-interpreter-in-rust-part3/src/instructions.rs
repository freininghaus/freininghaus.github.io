#[derive(Debug, PartialEq, Eq)]
pub enum Instruction {
    Inc,
    Dec,
    Left,
    Right,
    Read,
    Write,
    Loop(Vec<Instruction>),
}
