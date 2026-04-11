from enum import StrEnum


class Marker(StrEnum):
    O = "○"
    X = "×"


class Board:
    def __init__(self, size):
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.size = size

    def __str__(self):
        out = ""
        for row in range(self.size):
            for col in range(self.size):
                out += str(self.grid[row][col]) if self.grid[row][col] else "·"

                if col < self.size - 1:
                    out += " "

            if row < self.size - 1:
                out += "\n"

        return out

    def mark(self, marker, row, col):
        if row not in range(self.size) or col not in range(self.size):
            raise Exception("Cannot mark outside of board bounds")

        if self.grid[row][col]:
            raise Exception(f"Cell {row},{col} is already marked")

        self.grid[row][col] = marker

    def check_state(self):
        lines = []

        # Rows and columns
        for i in range(self.size):
            lines.append([self.grid[i][col] for col in range(self.size)])
            lines.append([self.grid[row][i] for row in range(self.size)])

        # Diagonals
        lines.append([self.grid[i][i] for i in range(self.size)])
        lines.append([self.grid[i][self.size - 1 - i] for i in range(self.size)])

        for line in lines:
            first = line[0]
            if first and all(marker == first for marker in line):
                return True, first

        # Draw
        flat = [marker for row in self.grid for marker in row]
        if all(marker for marker in flat):
            return True, None

        return False, None
