import struct
import csv
import argparse

# Команды виртуальной машины
COMMANDS = {
    'LOAD_CONST': 72,
    'READ_MEM': 19,
    'WRITE_MEM': 85,
    'SHIFT_RIGHT': 74
}

class Assembler:
    def assemble(self, source_path, binary_path, log_path):
        with open(source_path, 'r') as src, open(binary_path, 'wb') as bin_file, open(log_path, 'w', newline='') as log_file:
            log_writer = csv.writer(log_file)
            log_writer.writerow(["Command", "Opcode", "Operands"])

            for line in src:
                parts = line.strip().split()
                command = parts[0]
                opcode = COMMANDS.get(command)

                if opcode is None:
                    raise ValueError(f"Unknown command: {command}")

                operands = [int(x) for x in parts[1:]]
                instruction = struct.pack('B' + 'H' * len(operands), opcode, *operands)
                bin_file.write(instruction)

                log_writer.writerow([command, opcode, operands])

class Interpreter:
    def __init__(self):
        self.stack = []
        self.memory = {}

    def execute(self, binary_path, result_path, memory_range):
        with open(binary_path, 'rb') as bin_file, open(result_path, 'w', newline='') as res_file:
            result_writer = csv.writer(res_file)

            while instruction := bin_file.read(3):
                opcode, operand = struct.unpack('BH', instruction)

                if opcode == COMMANDS['LOAD_CONST']:
                    self.stack.append(operand)
                elif opcode == COMMANDS['READ_MEM']:
                    address = self.stack.pop() + operand
                    self.stack.append(self.memory.get(address, 0))
                elif opcode == COMMANDS['WRITE_MEM']:
                    value = self.stack.pop()
                    address = self.stack.pop()
                    self.memory[address] = value
                elif opcode == COMMANDS['SHIFT_RIGHT']:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.append(a >> b)

            for addr in range(*memory_range):
                result_writer.writerow([addr, self.memory.get(addr, 0)])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler and Interpreter for Virtual Machine")
    subparsers = parser.add_subparsers(dest="mode")

    assemble_parser = subparsers.add_parser("assemble")
    assemble_parser.add_argument("source", help="Path to source file")
    assemble_parser.add_argument("binary", help="Path to binary output file")
    assemble_parser.add_argument("log", help="Path to log file")

    interpret_parser = subparsers.add_parser("interpret")
    interpret_parser.add_argument("binary", help="Path to binary input file")
    interpret_parser.add_argument("result", help="Path to result file")
    interpret_parser.add_argument("--memory-range", type=int, nargs=2, required=True, help="Memory range to output")

    args = parser.parse_args()

    if args.mode == "assemble":
        assembler = Assembler()
        assembler.assemble(args.source, args.binary, args.log)
    elif args.mode == "interpret":
        interpreter = Interpreter()
        interpreter.execute(args.binary, args.result, args.memory_range)
