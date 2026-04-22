import sys

class Interpreter:

    def __init__(self):
        self.stack = []
        self.variables = {}
        self.instructions = []
        self.labels = {}  # label number -> instruction index
        self.ip = 0

    def load(self, code_text):
        for line in code_text.strip().splitlines():
            line = line.strip()
            if line:
                self.instructions.append(line)
        # Pre-scan labels so jumps work in any direction
        for i, instr in enumerate(self.instructions):
            parts = instr.split()
            if parts[0] == 'label':
                self.labels[int(parts[1])] = i

    def run(self):
        while self.ip < len(self.instructions):
            self._execute(self.instructions[self.ip])
            self.ip += 1

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _format(self, v):
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, float):
            # Print integers-valued floats with one decimal (e.g. 1.0, not 1)
            return str(v)
        return str(v)

    def _parse_string_literal(self, s):
        """Strip surrounding quotes from a push S value."""
        return s[1:-1]

    # ── Execution ─────────────────────────────────────────────────────────────

    def _execute(self, instr):
        # Split carefully: 'push S "hello world"' must keep value intact
        parts = instr.split(None, 2)
        op = parts[0]

        if op == 'push':
            T, val = parts[1], parts[2]
            if T == 'I':
                self.stack.append(int(val))
            elif T == 'F':
                self.stack.append(float(val))
            elif T == 'B':
                self.stack.append(val == 'true')
            elif T == 'S':
                self.stack.append(self._parse_string_literal(val))

        elif op == 'pop':
            self.stack.pop()

        elif op == 'load':
            self.stack.append(self.variables[parts[1]])

        elif op == 'save':
            self.variables[parts[1]] = self.stack.pop()

        elif op == 'add':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)

        elif op == 'sub':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)

        elif op == 'mul':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)

        elif op == 'div':
            b, a = self.stack.pop(), self.stack.pop()
            if parts[1] == 'I':
                self.stack.append(int(a / b))  # truncate toward zero
            else:
                self.stack.append(a / b)

        elif op == 'mod':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a % b)

        elif op == 'uminus':
            self.stack.append(-self.stack.pop())

        elif op == 'concat':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)

        elif op == 'and':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a and b)

        elif op == 'or':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a or b)

        elif op == 'gt':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a > b)

        elif op == 'lt':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a < b)

        elif op == 'eq':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a == b)

        elif op == 'not':
            self.stack.append(not self.stack.pop())

        elif op == 'itof':
            self.stack.append(float(self.stack.pop()))

        elif op == 'label':
            pass  # already handled in pre-scan

        elif op == 'jmp':
            # ip will be incremented by run(), so point to label instruction itself
            self.ip = self.labels[int(parts[1])]

        elif op == 'fjmp':
            if not self.stack.pop():
                self.ip = self.labels[int(parts[1])]

        elif op == 'print':
            n = int(parts[1])
            values = [self.stack.pop() for _ in range(n)]
            values.reverse()  # stack is LIFO, restore original push order
            print(''.join(self._format(v) for v in values))

        elif op == 'read':
            T = parts[1]
            line = sys.stdin.readline().rstrip('\n')
            if T == 'I':
                self.stack.append(int(line))
            elif T == 'F':
                self.stack.append(float(line))
            elif T == 'B':
                self.stack.append(line.strip() == 'true')
            elif T == 'S':
                self.stack.append(line)

        else:
            print(f"Unknown instruction: {op}", file=sys.stderr)
            sys.exit(1)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    interp = Interpreter()
    interp.load(code)
    interp.run()


if __name__ == '__main__':
    main()
