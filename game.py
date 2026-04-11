class Board:
    def __init__(self, row_size, col_size):
        self.grid = [[None for _ in range(col_size)] for _ in range(row_size)]
        self.row_size = row_size
        self.col_size = col_size

    def __str__(self):
        out = ""
        for row in range(self.row_size):
            for col in range(self.col_size):
                out += self.grid[row][col] if self.grid[row][col] else "·"
                out += " " if col < self.col_size - 1 else "\n"
        return out
