from game import Board, Mark


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
            mark = Mark.CIRCLE if player == 1 else Mark.CROSS

            print(f"[Turn {turn}] Player {player}")

            row = int(input("Row: "))
            col = int(input("Col: "))
            board.mark(mark, row, col)
            turn += 1

            print("\n")
            print(board)
        except Exception as e:
            print("\n")
            print(e)
        finally:
            print("\n")


if __name__ == "__main__":
    main()
