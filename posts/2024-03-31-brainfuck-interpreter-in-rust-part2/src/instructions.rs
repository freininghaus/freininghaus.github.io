#[derive(Debug)]
pub enum Instruction {
    Inc,
    Dec,
    Left,
    Right,
    Read,
    Write,
    Loop(Vec<Instruction>)
}
