from collections import deque
from enum import StrEnum


class Marker(StrEnum):
    O = "○"
    X = "×"


MARKER_OF = {1: Marker.O, 2: Marker.X}
PLAYER_OF = {Marker.O: 1, Marker.X: 2}


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


class GameStatus:
    PLAYING = 1
    WON = 2
    DRAW = 3


class GameState:
    def __init__(
        self,
        board,
        turn,
        decay_pos,
        current_player,
        status,
        winner,
    ):
        self.board = board
        self.turn = turn
        self.decay_pos = decay_pos
        self.current_player = current_player
        self.status = status
        self.winner = winner


class Game:
    def __init__(self):
        self.board = Board(3)
        self.marker_history = deque()
        self.turn = 1
        self.current_player = 1
        self.decaying = False

    def next_turn(self):
        if self.get_state().status != GameStatus.PLAYING:
            return

        self.turn += 1
        self.current_player = (self.turn - 1) % 2 + 1

        if self.decaying:
            self.decay()

        if self.turn > self.board.size * 2:
            self.decaying = True

    def mark(self, row, col):
        if not self.board.is_in_bounds(row, col):
            raise Exception("Cannot mark outside of board bounds")

        if self.board.is_marked(row, col):
            raise Exception(f"Cell is already marked")

        self.board.grid[row][col] = MARKER_OF[self.current_player]
        self.marker_history.append((row, col))

    def decay(self):
        # Get the oldest marker position
        decay_pos = self.marker_history.popleft()

        # Clear the marker at that position
        if decay_pos:
            row, col = decay_pos
            self.board.grid[row][col] = None

    def get_state(self):
        winning_marker = self._get_winning_marker()

        if winning_marker:
            status = GameStatus.WON
            winner = PLAYER_OF[winning_marker]
        elif self.board.is_full():
            status = GameStatus.DRAW
            winner = None
        else:
            status = GameStatus.PLAYING
            winner = None

        return GameState(
            board=self.board,
            turn=self.turn,
            decay_pos=(
                self.marker_history[0]
                if self.marker_history and self.decaying
                else None
            ),
            current_player=self.current_player,
            status=status,
            winner=winner,
        )

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
