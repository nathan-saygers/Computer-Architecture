"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 255
        self.halted = False
        self.registers = [0] * 8
        self.e = 0
        self.l = 0
        self.g = 0

        self.commands = {
            'HLT': 0b00000001,
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'MUL': 0b10100010,
            'PSH': 0b01000101,
            'POP': 0b01000110,
            'ADD': 0b10100000,
            'CAL': 0b01010000,
            'RET': 0b00010001,
            'JMP': 0b01010100,
            'JEQ': 0b01010101,
            'JNE': 0b01010110,
            'CMP': 0b10100111,
        }

    def load(self, file):
        """Load a program into ram."""

        prog_file = open(file, 'r')
        program = []

        for line in prog_file:
            line_arr = line.split(" ")
            if line_arr[0][0] == '1' or line_arr[0][0] == '0':
                # print("loading...", int(line_arr[0], 2))
                program.append(int(line_arr[0], 2))

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[self.pc] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 'ADD':
            self.registers[reg_a] += self.registers[reg_b]
            return

        if op == 'MUL':
            self.registers[reg_a] *= self.registers[reg_b]
            return

        if op == 'CMP':
            self.e = 0
            self.l = 0
            self.g = 0

            if self.registers[reg_a] == self.registers[reg_b]:
                self.e = 1
                return
            if self.registers[reg_a] > self.registers[reg_b]:
                self.g = 1
                return
            if self.registers[reg_a] < self.registers[reg_b]:
                self.l = 1
                return

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

    def run(self):
        while self.halted != True:
            # store ram slot at pc as instruction registry
            # store next two slots in case they are arguments
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            ir = self.ram[self.pc]

            if ir == self.commands['HLT']:
                self.halted = True

            elif ir == self.commands['LDI']:
                self.registers[operand_a] = operand_b
                self.pc += 3

            elif ir == self.commands['PRN']:
                print(self.registers[operand_a])
                self.pc += 2

            elif ir == self.commands['MUL']:
                self.alu(
                    'MUL', operand_a, operand_b)
                self.pc += 3

            elif ir == self.commands['ADD']:
                self.alu(
                    'ADD', operand_a, operand_b
                )
                self.pc += 3

            elif ir == self.commands['CMP']:
                self.alu(
                    'CMP', operand_a, operand_b
                )
                self.pc += 3

            elif ir == self.commands['PSH']:
                self.sp -= 1
                self.ram[self.sp] = self.registers[operand_a]
                self.pc += 2

            elif ir == self.commands['POP']:
                self.registers[operand_a] = self.ram[self.sp]
                self.pc += 2
                self.sp += 1

            elif ir == self.commands['CAL']:
                # save return address
                return_address = self.pc + 2
                # Push it onto the stack
                self.sp -= 1
                self.ram[self.sp] = return_address
                # Set the PC to the subroutine Address
                self.pc = self.registers[operand_a]

            elif ir == self.commands['RET']:
                # Pop the return address off the stack
                return_address = self.ram[self.sp]
                self.sp += 1
                # set pc to return address
                self.pc = return_address

            elif ir == self.commands['JMP']:
                self.pc = self.registers[operand_a]

            elif ir == self.commands['JEQ']:
                if self.e == 1:
                    self.pc = self.registers[operand_a]
                else:
                    self.pc += 2

            elif ir == self.commands['JNE']:
                if self.e == 0:
                    self.pc = self.registers[operand_a]
                else:
                    self.pc += 2

            else:
                print(
                    f'unknown instruction at address {self.pc}')
                sys.exit(1)
