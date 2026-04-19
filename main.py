import random
import selectors
import sys

from enum import Enum

import src.game as game
import src.network as network
import src.ui as ui


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

                    server_sock = network.start_server()

                    if not server_sock:
                        screen = Screen.MAIN_MENU
                        continue

                    sel = selectors.DefaultSelector()
                    sel.register(sys.stdin, selectors.EVENT_READ, data="stdin")
                    sel.register(server_sock, selectors.EVENT_READ, data="socket")

                    while True:
                        stop_selector = False

                        for key, _ in sel.select():
                            match key.data:
                                case "socket":
                                    sock, _ = server_sock.accept()

                                    if sock:
                                        player_1 = random.choice([True, False])
                                        network.send_payload(
                                            sock,
                                            network.PayloadType.SET_PLAYER,
                                            not player_1,
                                        )

                                        curr_sock, curr_player_1 = sock, player_1
                                        screen = Screen.GAME

                                        stop_selector = True
                                        break

                                case "stdin":
                                    char = sys.stdin.read(1)
                                    key = ui.handle_server_starting_input(char)

                                    if key == ui.Key.EXIT:
                                        screen = Screen.MAIN_MENU

                                        stop_selector = True
                                        break

                        if stop_selector:
                            sel.close()
                            server_sock.close()
                            break

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
    curr_game = game.Game()
    cursor_pos = game.Pos(0, 0)
    error = None
    needs_redraw = True

    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ, data="stdin")
    sel.register(sock, selectors.EVENT_READ, data="socket")

    try:
        while True:
            game_state = curr_game.get_state()
            should_exit = game_state.status != game.GameStatus.PLAYING or error

            if needs_redraw:
                ui.draw_game(game_state, cursor_pos, player_1, should_exit, error)
                needs_redraw = False

            if should_exit:
                # Block only on stdin, ignore socket events
                for key, _ in sel.select():
                    if key.data == "stdin":
                        sys.stdin.read(1)
                        network.send_payload(sock, network.PayloadType.EXIT)
                        return

                continue

            our_turn = (game_state.current_player == 1) == player_1

            for key, _ in sel.select():
                match key.data:
                    case "socket":
                        payload = network.receive_payload(sock)

                        if not payload:
                            error = "Opponent has disconnected"
                            needs_redraw = True
                            break

                        type, data = payload
                        match type:
                            case network.PayloadType.MARK:
                                row, col = data[0], data[1]
                                curr_game.mark(game.Pos(row, col))
                                curr_game.next_turn()
                                needs_redraw = True

                            case network.PayloadType.EXIT:
                                error = "Opponent has quit the game"
                                needs_redraw = True

                    case "stdin":
                        char = sys.stdin.read(1)
                        if char == "\x1b":
                            char += sys.stdin.read(2)

                        key = ui.handle_game_input(char, game_state, cursor_pos)

                        if not our_turn and key == ui.Key.EXIT:
                            network.send_payload(sock, network.PayloadType.EXIT)
                            return

                        match key:
                            case ui.Key.CURSOR_UP:
                                cursor_pos = cursor_pos.translated(-1, 0)
                                needs_redraw = True

                            case ui.Key.CURSOR_DOWN:
                                cursor_pos = cursor_pos.translated(1, 0)
                                needs_redraw = True

                            case ui.Key.CURSOR_LEFT:
                                cursor_pos = cursor_pos.translated(0, -1)
                                needs_redraw = True

                            case ui.Key.CURSOR_RIGHT:
                                cursor_pos = cursor_pos.translated(0, 1)
                                needs_redraw = True

                            case ui.Key.SELECT:
                                curr_game.mark(cursor_pos)
                                network.send_payload(
                                    sock,
                                    network.PayloadType.MARK,
                                    cursor_pos.row,
                                    cursor_pos.col,
                                )
                                curr_game.next_turn()
                                needs_redraw = True

                            case ui.Key.EXIT:
                                network.send_payload(sock, network.PayloadType.EXIT)
                                return
    finally:
        sel.close()


if __name__ == "__main__":
    main()
