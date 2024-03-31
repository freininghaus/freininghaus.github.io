use std::collections::VecDeque;

#[derive(Debug)]
pub struct Tape {
    data: VecDeque<u8>,
    pos: usize
}

impl Tape {
    pub fn new() -> Self {
        Self{
            data: VecDeque::from([0]),
            pos: 0
        }
    }

    pub fn get(&self) -> u8 {
        self.data[self.pos]
    }

    pub fn set(&mut self, value: u8) {
        self.data[self.pos] = value;
    }

    pub fn right(&mut self) {
        self.pos += 1;
        if self.pos == self.data.len() {
            // The data pointer is moving off the tape:
            // add a new zero-valued cell at the back.
            self.data.push_back(0);
        }
    }

    pub fn left(&mut self) {
        if self.pos > 0 {
            // We have not reached the leftmost cell yet.
            // Just move the data pointer to the left.
            self.pos -= 1
        } else {
            // If self.pos is 0, the data pointer points to the leftmost cell.
            // Add a new cell at the front and leave the pointer as it is.
            self.data.push_front(0);
        }
    }
}
