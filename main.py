import random

from game import Game, GameStatus
from network import (
    start_server,
    connect_server,
    get_ip,
    send_payload,
    receive_payload,
    PayloadType,
)
from renderer import raw_mode, render, KEY


# TODO: Handle socket and key presses simultaneously, use select?

# TODO: Render the whole program in raw mode


def main():
    while True:
        print("Welcome to Tic Tac Two!\n")

        print("(1) Start a game server")
        print("(2) Connect to a game server")
        print("(q) Quit")

        option = input("\nSelect an option: ")
        print("")

        match option:
            case "1":
                server_ip = get_ip()
                print(f"Server IP: {server_ip}")
                print("Waiting for connection...")

                sock = start_server()

                player_1 = random.choice([True, False])
                send_payload(sock, PayloadType.SET_PLAYER, not player_1)

                if sock:
                    init_game(sock, player_1)

            case "2":
                server_ip = input("Server IP: ")
                sock = connect_server(server_ip)

                payload = receive_payload(sock)

                if payload and payload[0] == PayloadType.SET_PLAYER:
                    player_1 = payload[1]

                if sock:
                    init_game(sock, player_1)

            case "q":
                exit()

            case _:
                print("Please select a valid option.\n")


def init_game(sock, player_1):
    # Initialize game
    game = Game()

    # Enter terminal raw mode, automatically restore on finish
    with raw_mode():
        # Current cursor position at [row, col]
        cursor = [0, 0]

        while True:
            state = game.get_state()

            our_turn = (state.current_player == 1) == player_1

            key = render(state, cursor, player_1)

            # If opponent's turn and game not yet finished, wait for their action and handle
            if not our_turn and state.status == GameStatus.PLAYING:
                payload = receive_payload(sock)

                if not payload:
                    print("Opponent has disconnected\r\n")
                    exit()

                type, data = payload

                match type:
                    case PayloadType.MARK:
                        row, col = data[0], data[1]
                        game.mark(row, col)
                        game.next_turn()
                        
                    case PayloadType.EXIT:
                        print("Opponent has exited the game\r\n")
                        exit()

                continue

            # Otherwise, handle inputs
            match key:
                case KEY.CURSOR_UP:
                    if cursor[0] > 0:
                        cursor[0] -= 1

                case KEY.CURSOR_DOWN:
                    if cursor[0] < state.board.size - 1:
                        cursor[0] += 1

                case KEY.CURSOR_LEFT:
                    if cursor[1] > 0:
                        cursor[1] -= 1

                case KEY.CURSOR_RIGHT:
                    if cursor[1] < state.board.size - 1:
                        cursor[1] += 1

                case KEY.SELECT:
                    game.mark(cursor[0], cursor[1])
                    send_payload(sock, PayloadType.MARK, cursor[0], cursor[1])
                    game.next_turn()

                case KEY.EXIT:
                    send_payload(sock, PayloadType.EXIT)
                    break


if __name__ == "__main__":
    main()
