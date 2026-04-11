from enum import StrEnum


class Mark(StrEnum):
    CIRCLE = "○"
    CROSS = "×"


class Board:
    def __init__(self, row_size, col_size):
        self.grid = [[None for _ in range(col_size)] for _ in range(row_size)]
        self.row_size = row_size
        self.col_size = col_size

    def __str__(self):
        out = ""
        for row in range(self.row_size):
            for col in range(self.col_size):
                out += str(self.grid[row][col]) if self.grid[row][col] else "·"

                if col < self.col_size - 1:
                    out += " "

            if row < self.row_size - 1:
                out += "\n"

        return out

    def mark(self, mark, row, col):
        if row not in range(self.row_size) or col not in range(self.col_size):
            raise Exception("Cannot mark outside of board bounds")

        if self.grid[row][col]:
            raise Exception(f"Cell {row},{col} is already marked")

        self.grid[row][col] = mark
