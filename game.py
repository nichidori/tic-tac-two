from enum import StrEnum


class Mark(StrEnum):
    CIRCLE = "○"
    CROSS = "×"


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

    def mark(self, mark, row, col):
        if row not in range(self.size) or col not in range(self.size):
            raise Exception("Cannot mark outside of board bounds")

        if self.grid[row][col]:
            raise Exception(f"Cell {row},{col} is already marked")

        self.grid[row][col] = mark
