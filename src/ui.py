import sys
import tty
import termios

from enum import Enum
from contextlib import contextmanager

from src.game import GameStatus, Marker, MARKER_OF, Pos

HLINE = "\u2501"
VLINE = "\u2503"
PLUS = "\u254b"

RESET = "\033[0m"

COLOR_OF = {Marker.O: "\033[32m", Marker.X: "\033[34m"}


class Key(Enum):
    CURSOR_UP = 1
    CURSOR_DOWN = 2
    CURSOR_LEFT = 3
    CURSOR_RIGHT = 4
    SELECT = 5
    START_SERVER = 97
    START_CLIENT = 98
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
        # Clear terminal
        clear_screen()

        # Show cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

        # Restore terminal state
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)


def draw_main_menu():
    clear_screen()

    sys.stdout.write(
        """
 _____ _     _____         _____                   \r
|_   _(_) __|_   _|_ _  __|_   _|_      _____      \r
  | | | |/ __|| |/ _` |/ __|| | \ \ /\ / / _ \     \r
  | | | | (__ | | (_| | (__ | |  \ V  V / (_) |    \r
  |_| |_|\___||_|\__,_|\___||_|   \_/\_/ \___/     \r
\r\n\r\n"""
    )

    sys.stdout.write("Please select an option:\r\n")
    sys.stdout.write("(1) Start a game server\r\n")
    sys.stdout.write("(2) Connect to a game server\r\n")
    sys.stdout.write("(q) Quit\r\n")


def draw_server_starting(server_ip):
    clear_screen()

    sys.stdout.write(f"Server IP: {server_ip}\r\n")
    sys.stdout.write("Waiting for connection...\r\n\r\n")

    # Push the entire frame to the screen at once
    sys.stdout.flush()


# TODO: Reimplement server IP input


def draw_client_starting(server_ip=None):
    clear_screen()

    connecting_msg = (
        "Connecting to server at {server_ip}..."
        if server_ip
        else "Connecting to local server..."
    )
    sys.stdout.write(f"{connecting_msg}\r\n\r\n")

    # Push the entire frame to the screen at once
    sys.stdout.flush()


def draw_game(game_state, cursor_pos, player_1, should_exit, error):
    clear_screen()

    board = game_state.board
    current_player_color = COLOR_OF[MARKER_OF[game_state.current_player]]

    our_turn = (game_state.current_player == 1) == player_1
    turn = "Your Turn" if our_turn else "Opponent Turn"

    sys.stdout.write(f"[Turn {game_state.turn}]")
    sys.stdout.write(f"{current_player_color} {turn}{RESET}\r\n\r\n\r\n")

    # Draw board
    for row in range(board.size):
        for col in range(board.size):
            marker = board.grid[row][col]
            marker_char = str(marker) if marker else " "

            color = (
                COLOR_OF[marker]
                if marker and Pos(row, col) != game_state.decay_pos
                else ""
            )

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
    board_org_row = 4
    board_org_col = 0

    # Draw cursor at selected cell if our turn
    if our_turn:
        cursor_row = board_org_row + (cursor_pos.row * 2)
        cursor_col = board_org_col + (cursor_pos.col * 4) + 1
        sys.stdout.write(f"\033[{cursor_row};{cursor_col}H")
        sys.stdout.write("[")
        sys.stdout.write(f"\033[{cursor_row};{cursor_col+2}H")
        sys.stdout.write("]")

    # Go to position after board end
    sys.stdout.write(f"\033[{board_org_row + (board.size * 2) - 1};{0}H")
    sys.stdout.write("\r\n\r\n")

    if not our_turn:
        sys.stdout.write(f"Waiting for opponent move...\r\n\r\n")

    match game_state.status:
        case GameStatus.WON:
            winner = "You" if (game_state.winner == 1) == player_1 else "Opponent"
            winner_color = COLOR_OF[MARKER_OF[game_state.winner]]
            sys.stdout.write(f"{winner_color}{winner} won!{RESET}\r\n")

        case GameStatus.DRAW:
            sys.stdout.write(f"Draw!\r\n")

    if error:
        sys.stdout.write(f"{error}\r\n")

    if should_exit:
        sys.stdout.write("Press any key to exit\r\n")

    # Push the entire frame to the screen at once
    sys.stdout.flush()


def clear_screen():
    # Jump to top and clear to end
    sys.stdout.write("\033[H\033[J")


def handle_main_menu_input(char):
    match char:
        case "1":
            key = Key.START_SERVER
        case "2":
            key = Key.START_CLIENT
        case "q" | "\x03":
            key = Key.EXIT
        case _:
            key = None

    return key


def handle_server_starting_input(char):
    return Key.EXIT if char == "\x03" else None


def handle_client_starting_input(char):
    return Key.EXIT if char == "\x03" else None


def handle_game_input(char, game_state, cursor_pos):
    match char:
        # Arrow keys
        case "\x1b[A":
            key = Key.CURSOR_UP
        case "\x1b[B":
            key = Key.CURSOR_DOWN
        case "\x1b[C":
            key = Key.CURSOR_RIGHT
        case "\x1b[D":
            key = Key.CURSOR_LEFT

        # WASD
        case "w":
            key = Key.CURSOR_UP
        case "s":
            key = Key.CURSOR_DOWN
        case "a":
            key = Key.CURSOR_LEFT
        case "d":
            key = Key.CURSOR_RIGHT

        # Enter
        case "\r":
            key = Key.SELECT

        # Ctrl+C
        case "\x03":
            key = Key.EXIT

        case _:
            key = None

    # Prevent marking if cell is already marked
    if key == Key.SELECT and game_state.board.is_marked(cursor_pos):
        key = None

    # Prevent cursor from going out of bounds
    if (
        (key == Key.CURSOR_UP and cursor_pos.row == 0)
        or (key == Key.CURSOR_DOWN and cursor_pos.row == game_state.board.size - 1)
        or (key == Key.CURSOR_LEFT and cursor_pos.col == 0)
        or (key == Key.CURSOR_RIGHT and cursor_pos.col == game_state.board.size - 1)
    ):
        key = None

    return key
