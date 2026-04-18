import random
import sys

from enum import Enum

import src.game as game
import src.network as network
import src.ui as ui


# TODO: Handle socket and key presses simultaneously, use select?


class Screen(Enum):
    MAIN_MENU = 1
    SERVER_STARTING = 2
    CLIENT_STARTING = 3
    GAME = 4


def main():
    screen = Screen.MAIN_MENU

    # Session data
    curr_sock, curr_player_1 = None, None

    # Enter terminal raw mode, automatically restore on finish
    with ui.raw_mode():
        while True:
            match screen:
                case Screen.MAIN_MENU:
                    ui.draw_main_menu()

                    char = sys.stdin.read(1)
                    key = ui.handle_main_menu_input(char)

                    match key:
                        case ui.Key.START_SERVER:
                            screen = Screen.SERVER_STARTING

                        case ui.Key.START_CLIENT:
                            screen = Screen.CLIENT_STARTING

                        case ui.Key.EXIT:
                            exit()

                case Screen.SERVER_STARTING:
                    server_ip = network.get_ip()

                    ui.draw_server_starting(server_ip)

                    sock = network.start_server()

                    if sock:
                        player_1 = random.choice([True, False])
                        network.send_payload(
                            sock,
                            network.PayloadType.SET_PLAYER,
                            not player_1,
                        )

                        curr_sock, curr_player_1 = sock, player_1
                        screen = Screen.GAME

                case Screen.CLIENT_STARTING:
                    ui.draw_client_starting()

                    sock = network.connect_server()

                    if sock:
                        payload = network.receive_payload(sock)

                        if payload and payload[0] == network.PayloadType.SET_PLAYER:
                            player_1 = payload[1]

                        curr_sock, curr_player_1 = sock, player_1
                        screen = Screen.GAME

                case Screen.GAME:
                    init_game(curr_sock, curr_player_1)

                    curr_sock.close()
                    curr_sock, curr_player_1 = None, None
                    screen = Screen.MAIN_MENU


def init_game(sock, player_1):
    # Initialize game state
    curr_game = game.Game()
    cursor_pos = game.Pos(0, 0)
    error = None

    while True:
        game_state = curr_game.get_state()

        # Check if game should not continue
        should_exit = game_state.status != game.GameStatus.PLAYING or error

        ui.draw_game(game_state, cursor_pos, player_1, should_exit, error)

        our_turn = (game_state.current_player == 1) == player_1

        # If opponent's turn and game not yet finished, wait for their action and handle
        if (
            not our_turn
            and game_state.status == game.GameStatus.PLAYING
            and not should_exit
        ):
            payload = network.receive_payload(sock)

            if not payload:
                error = "Opponent has disconnected"
                continue

            type, data = payload

            match type:
                case network.PayloadType.MARK:
                    row, col = data[0], data[1]
                    curr_game.mark(game.Pos(row, col))
                    curr_game.next_turn()

                case network.PayloadType.EXIT:
                    error = "Opponent has quit the game"

            continue

        # Otherwise, handle inputs
        char = sys.stdin.read(1)

        # If we hit an escape character, check for an arrow sequence
        if char == "\x1b":
            # Read the next 2 bytes ('[' and the direction letter)
            char += sys.stdin.read(2)

        key = ui.handle_game_input(char, game_state, cursor_pos)

        if should_exit:
            key = ui.Key.EXIT

        match key:
            # TODO: Move bound checking to input handler

            case ui.Key.CURSOR_UP:
                if cursor_pos.row > 0:
                    cursor_pos = cursor_pos.translated(-1, 0)

            case ui.Key.CURSOR_DOWN:
                if cursor_pos.row < game_state.board.size - 1:
                    cursor_pos = cursor_pos.translated(1, 0)

            case ui.Key.CURSOR_LEFT:
                if cursor_pos.col > 0:
                    cursor_pos = cursor_pos.translated(0, -1)

            case ui.Key.CURSOR_RIGHT:
                if cursor_pos.col < game_state.board.size - 1:
                    cursor_pos = cursor_pos.translated(0, 1)

            case ui.Key.SELECT:
                curr_game.mark(cursor_pos)
                network.send_payload(
                    sock, network.PayloadType.MARK, cursor_pos.row, cursor_pos.col
                )
                curr_game.next_turn()

            case ui.Key.EXIT:
                network.send_payload(sock, network.PayloadType.EXIT)
                break


if __name__ == "__main__":
    main()
