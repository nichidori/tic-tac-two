import random
import selectors
import sys
import time

from enum import Enum

import src.game as game
import src.network as network
import src.ui as ui


class Screen(Enum):
    MAIN_MENU = 1
    SERVER_STARTING = 2
    CLIENT_STARTING = 3
    GAME = 4


class Session:
    def __init__(self, sock, player_1):
        self.sock = sock
        self.player_1 = player_1

    def close(self):
        self.sock.close()


def main():
    screen = Screen.MAIN_MENU
    curr_session = None

    # Enter terminal raw mode, automatically restore on finish
    with ui.raw_mode():
        while True:
            match screen:
                case Screen.MAIN_MENU:
                    next_screen = run_main_menu()

                    if next_screen:
                        screen = next_screen

                case Screen.SERVER_STARTING:
                    session = run_server_starting()

                    if not session:
                        screen = Screen.MAIN_MENU
                        continue

                    curr_session = session
                    screen = Screen.GAME

                case Screen.CLIENT_STARTING:
                    session = run_client_starting()

                    if not session:
                        screen = Screen.MAIN_MENU
                        continue

                    curr_session = session
                    screen = Screen.GAME

                case Screen.GAME:
                    run_game(curr_session)

                    curr_session.close()
                    curr_session = None
                    screen = Screen.MAIN_MENU


def run_main_menu():
    ui.draw_main_menu()

    char = sys.stdin.read(1)
    key = ui.handle_main_menu_input(char)

    match key:
        case ui.Key.START_SERVER:
            return Screen.SERVER_STARTING

        case ui.Key.START_CLIENT:
            return Screen.CLIENT_STARTING

        case ui.Key.EXIT:
            exit()

    return None


def run_server_starting():
    server_ip = network.get_ip()

    ui.draw_server_starting(server_ip)

    server_sock = network.start_server()

    if not server_sock:
        return None

    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ, data="stdin")
    sel.register(server_sock, selectors.EVENT_READ, data="socket")

    finish = False
    session = None

    while not finish:
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

                        session = Session(sock, player_1)
                        finish = True

                case "stdin":
                    char = sys.stdin.read(1)
                    key = ui.handle_server_starting_input(char)

                    if key == ui.Key.EXIT:
                        finish = True

    sel.close()
    server_sock.close()

    return session


def run_client_starting():
    server_ip = ""
    input_set = False

    # Handle server ip input
    while not input_set:
        ui.draw_client_starting(server_ip, input_set)

        char = sys.stdin.read(1)

        # Ignore input if it start with escape character
        if char == "\x1b":
            sys.stdin.read(2)
            continue

        key = ui.handle_client_starting_input(char)

        match key:
            case ui.Key.SELECT:
                input_set = True

            case ui.Key.DELETE:
                if server_ip:
                    server_ip = server_ip[:-1]

            case ui.Key.EXIT:
                return None

            case _ if isinstance(key, str):
                server_ip += char

    ui.draw_client_starting(server_ip, input_set)

    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ, data="stdin")

    finish = False
    session = None

    while not finish:
        # Delay before connection to show loading state and
        # avoid too many reconnection
        time.sleep(0.5)

        server_ip = server_ip if server_ip else "127.0.0.1"
        sock = network.connect_server(server_ip)

        if sock:
            sel.register(sock, selectors.EVENT_READ, data="socket")

            for key, _ in sel.select():
                match key.data:
                    case "socket":
                        payload = network.receive_payload(sock)

                        if payload and payload[0] == network.PayloadType.SET_PLAYER:
                            player_1 = payload[1]

                            session = Session(sock, player_1)
                        else:
                            sock.close()

                        finish = True

                    case "stdin":
                        char = sys.stdin.read(1)
                        key = ui.handle_client_starting_input(char)

                        if key == ui.Key.EXIT:
                            sock.close()
                            finish = True

            sel.unregister(sock)

        else:
            for key, _ in sel.select(timeout=0):
                if key.data == "stdin":
                    char = sys.stdin.read(1)
                    key = ui.handle_client_starting_input(char)

                    if key == ui.Key.EXIT:
                        finish = True

    sel.close()

    return session


def run_game(session):
    sock = session.sock
    player_1 = session.player_1

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
