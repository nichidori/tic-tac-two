import sys
import tty
import termios

from enum import Enum
from contextlib import contextmanager

from game import GameStatus, Marker, MARKER_OF

HLINE = "\u2501"
VLINE = "\u2503"
PLUS = "\u254b"

RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"

COLOR_OF = {Marker.O: RED, Marker.X: BLUE}


class KEY(Enum):
    CURSOR_UP = 1
    CURSOR_DOWN = 2
    CURSOR_LEFT = 3
    CURSOR_RIGHT = 4
    SELECT = 5
    EXIT = 99


@contextmanager
def raw_mode():
    # Get standard input file descriptor
    fd = sys.stdin.fileno()

    # Store current terminal state to be restored later
    old_attrs = termios.tcgetattr(fd)

    try:
        # Enter raw mode
        tty.setraw(fd)

        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        yield

    finally:
        # Show cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

        # Restore terminal state
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)


def render(state, cursor):
    board = state.board

    # Jump to top and clear to end
    sys.stdout.write("\033[H\033[J")

    sys.stdout.write("Tic Tac Two started!\r\n")
    sys.stdout.write("Press Ctrl+C to quit\r\n\r\n\r\n")

    player_color = COLOR_OF[MARKER_OF[state.current_player]]

    sys.stdout.write(f"[Turn {state.turn}]")
    sys.stdout.write(f"{player_color} Player {state.current_player}{RESET}\r\n\r\n\r\n")

    # Draw board
    for row in range(board.size):
        for col in range(board.size):
            marker = board.grid[row][col]
            marker_char = str(marker) if marker else " "
            color = COLOR_OF[marker] if marker and (row, col) != state.decay_pos else ""
            sys.stdout.write(f"{color} {marker_char} {RESET}")

            if col < board.size - 1:
                sys.stdout.write(VLINE)

        if row < board.size - 1:
            sys.stdout.write("\r\n")

            for col in range(board.size):
                sys.stdout.write(HLINE * 3)

                if col < board.size - 1:
                    sys.stdout.write(PLUS)

            sys.stdout.write("\r\n")

    # Board top left position
    board_org_row = 8
    board_org_col = 0

    # Draw cursor at selected cell
    cursor_row = board_org_row + (cursor[0] * 2)
    cursor_col = board_org_col + (cursor[1] * 4) + 1
    sys.stdout.write(f"\033[{cursor_row};{cursor_col}H")
    sys.stdout.write("[")
    sys.stdout.write(f"\033[{cursor_row};{cursor_col+2}H")
    sys.stdout.write("]")

    # Go to position after board end
    sys.stdout.write(f"\033[{board_org_row + (board.size * 2) - 1};{0}H")
    sys.stdout.write("\r\n\r\n")

    match state.status:
        case GameStatus.WON:
            winner_color = COLOR_OF[MARKER_OF[state.winner]]
            sys.stdout.write(f"{winner_color}Player {state.winner}{RESET} won!\r\n")
            sys.stdout.write("Press any key to exit\r\n")

        case GameStatus.DRAW:
            sys.stdout.write(f"Draw!\r\n")
            sys.stdout.write("Press any key to exit\r\n")

    # Push the entire frame to the screen at once
    sys.stdout.flush()

    # Read input
    key = read_key()

    # If game finished, exit on any key press
    if state.status != GameStatus.PLAYING:
        return KEY.EXIT

    return key


def read_key():
    char = sys.stdin.read(1)

    # If we hit an escape character, check for an arrow sequence
    if char == "\x1b":
        # Read the next 2 bytes ('[' and the direction letter)
        char += sys.stdin.read(2)

    match char:
        # Arrow keys
        case "\x1b[A":
            return KEY.CURSOR_UP
        case "\x1b[B":
            return KEY.CURSOR_DOWN
        case "\x1b[C":
            return KEY.CURSOR_RIGHT
        case "\x1b[D":
            return KEY.CURSOR_LEFT

        # WASD
        case "w":
            return KEY.CURSOR_UP
        case "s":
            return KEY.CURSOR_DOWN
        case "a":
            return KEY.CURSOR_LEFT
        case "d":
            return KEY.CURSOR_RIGHT

        # Enter
        case "\r":
            return KEY.SELECT

        # Ctrl+C
        case "\x03":
            return KEY.EXIT
