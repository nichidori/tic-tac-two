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

    def is_in_bounds(self, row, col):
        return row in range(self.size) and col in range(self.size)

    def is_marked(self, row, col):
        return self.grid[row][col] is not None

    def is_full(self):
        return all(marker for row in self.grid for marker in row)


class Game:
    def __init__(self):
        self.board = Board(3)
        self.turn = 1
        self.current_player = 1

    def next_turn(self):
        self.turn += 1
        self.current_player = (self.turn - 1) % 2 + 1

    def mark(self, row, col):
        marker = Marker.O if self.current_player == 1 else Marker.X

        if not self.board.is_in_bounds(row, col):
            raise Exception("Cannot mark outside of board bounds")

        if self.board.is_marked(row, col):
            raise Exception(f"Cell is already marked")

        self.board.grid[row][col] = marker

    def get_state(self):
        winning_marker = self._get_winning_marker()

        if winning_marker:
            return True, 1 if winning_marker == Marker.O else 2

        if self.board.is_full():
            return True, None

        return False, None

    def _get_winning_marker(self):
        lines = []
        size = self.board.size

        # Check lines in rows and columns
        for i in range(size):
            lines.append([self.board.grid[i][col] for col in range(size)])
            lines.append([self.board.grid[row][i] for row in range(size)])

        # Check lines in diagonals
        lines.append([self.board.grid[i][i] for i in range(size)])
        lines.append([self.board.grid[i][size - 1 - i] for i in range(size)])

        for line in lines:
            first = line[0]
            if first and all(marker == first for marker in line):
                return first

        return None
