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
        n_marker = 0
        winning_marker = None

        # Find lines in rows
        for row in range(self.size):
            n_o = 0
            n_x = 0

            for col in range(self.size):
                match self.grid[row][col]:
                    case Marker.O:
                        n_marker += 1
                        n_o += 1

                    case Marker.X:
                        n_marker += 1
                        n_x += 1

            if n_o == self.size:
                winning_marker = Marker.O
                break

            if n_x == self.size:
                winning_marker = Marker.X
                break

        # Check if draw
        if n_marker == self.size * self.size:
            return True, None

        # Check if line found in row
        if winning_marker:
            return True, winning_marker

        # Check lines in columns
        for col in range(self.size):
            n_o = 0
            n_x = 0

            for row in range(self.size):
                match self.grid[row][col]:
                    case Marker.O:
                        n_o += 1

                    case Marker.X:
                        n_x += 1

            if n_o == self.size:
                winning_marker = Marker.O
                break

            if n_x == self.size:
                winning_marker = Marker.X
                break

        # Check if lines found in columns
        if winning_marker:
            return True, winning_marker

        # Find lines in diagonals
        n_main_diag_o = 0
        n_main_diag_x = 0
        n_anti_diag_o = 0
        n_anti_diag_x = 0

        for i in range(self.size):
            match self.grid[i][i]:
                case Marker.O:
                    n_main_diag_o += 1

                case Marker.X:
                    n_main_diag_x += 1

            match self.grid[i][self.size - 1 - i]:
                case Marker.O:
                    n_anti_diag_o += 1

                case Marker.X:
                    n_anti_diag_x += 1

        # Check if lines found in diagonals
        if n_main_diag_o == self.size or n_anti_diag_o == self.size:
            return True, Marker.O

        if n_main_diag_x == self.size or n_anti_diag_x == self.size:
            return True, Marker.X

        return False, None
