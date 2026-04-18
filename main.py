import random
import sys

from enum import Enum

import src.game as game
import src.network as network
import src.renderer as renderer


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
    with renderer.raw_mode():
        while True:
            match screen:
                case Screen.MAIN_MENU:
                    renderer.draw_main_menu()

                    char = sys.stdin.read(1)
                    key = renderer.handle_main_menu_input(char)

                    match key:
                        case renderer.Key.START_SERVER:
                            screen = Screen.SERVER_STARTING

                        case renderer.Key.START_CLIENT:
                            screen = Screen.CLIENT_STARTING

                        case renderer.Key.EXIT:
                            exit()

                case Screen.SERVER_STARTING:
                    server_ip = network.get_ip()

                    renderer.draw_server_starting(server_ip)

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
                    renderer.draw_client_starting()

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
    cursor = [0, 0]
    error = None

    while True:
        state = curr_game.get_state()

        # Check if game should not continue
        should_exit = state.status != game.GameStatus.PLAYING or error

        renderer.draw_game(state, cursor, player_1, should_exit, error)

        our_turn = (state.current_player == 1) == player_1

        # If opponent's turn and game not yet finished, wait for their action and handle
        if not our_turn and state.status == game.GameStatus.PLAYING and not should_exit:
            payload = network.receive_payload(sock)

            if not payload:
                error = "Opponent has disconnected"
                continue

            type, data = payload

            match type:
                case network.PayloadType.MARK:
                    row, col = data[0], data[1]
                    curr_game.mark(row, col)
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

        key = renderer.handle_game_input(char, state, cursor)

        if should_exit:
            key = renderer.Key.EXIT

        match key:
            # TODO: Move bound checking to input handler

            case renderer.Key.CURSOR_UP:
                if cursor[0] > 0:
                    cursor[0] -= 1

            case renderer.Key.CURSOR_DOWN:
                if cursor[0] < state.board.size - 1:
                    cursor[0] += 1

            case renderer.Key.CURSOR_LEFT:
                if cursor[1] > 0:
                    cursor[1] -= 1

            case renderer.Key.CURSOR_RIGHT:
                if cursor[1] < state.board.size - 1:
                    cursor[1] += 1

            case renderer.Key.SELECT:
                curr_game.mark(cursor[0], cursor[1])
                network.send_payload(
                    sock, network.PayloadType.MARK, cursor[0], cursor[1]
                )
                curr_game.next_turn()

            case renderer.Key.EXIT:
                network.send_payload(sock, network.PayloadType.EXIT)
                break


if __name__ == "__main__":
    main()
