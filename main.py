from game import Board, Marker


def main():
    print("Starting Tic Tac Two...\n")

    # Initialize board
    board = Board(3)
    print(board)
    print("\n")

    # Game loop
    turn = 1
    while True:
        try:
            player = ((turn - 1) % 2) + 1
            mark = Marker.O if player == 1 else Marker.X

            print(f"[Turn {turn}] Player {player}")

            row = int(input("Row: "))
            col = int(input("Col: "))
            board.mark(mark, row, col)
            turn += 1

            print("\n")
            print(board)

            finished, winning_marker = board.check_state()
            if finished:
                print("\n")

                if winning_marker:
                    winning_player = 1 if winning_marker == Marker.O else 2
                    print(f"Player {winning_player} win!")

                else:
                    print(f"Draw!")

                break

        except Exception as e:
            print("\n")
            print(e)
        finally:
            print("\n")


if __name__ == "__main__":
    main()
