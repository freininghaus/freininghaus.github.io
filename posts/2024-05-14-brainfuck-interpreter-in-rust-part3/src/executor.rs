use std::io::{Read, Write};

use crate::instructions::{Instruction, Instruction::*};
use crate::tape::Tape;

pub fn execute<R: Read, W: Write>(
    instructions: &[Instruction],
    input: &mut R,
    output: &mut W,
) {
    execute_with_tape(&mut Tape::new(), instructions, input, output);
}

pub fn execute_with_tape<R: Read, W: Write>(
    tape: &mut Tape,
    instructions: &[Instruction],
    input: &mut R,
    output: &mut W,
) {
    for instruction in instructions {
        match instruction {
            Left => tape.left(),
            Right => tape.right(),
            Inc => tape.set(tape.get() + 1),
            Dec => tape.set(tape.get() - 1),
            Loop(body) => {
                while tape.get() != 0 {
                    execute_with_tape(tape, body, input, output)
                }
            }
            Read => {
                let mut buf: [u8; 1] = [0];
                input.read_exact(&mut buf).unwrap();
                tape.set(buf[0])
            }
            Write => {
                output.write(&[tape.get()]).unwrap();
            }
        }
    }
}
