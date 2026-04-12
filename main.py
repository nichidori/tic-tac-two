from game import Game


def main():
    print("Starting Tic Tac Two...\n")

    # Initialize game
    game = Game()
    print(game.board)
    print("\n")

    # Game loop
    while True:
        try:
            print(f"[Turn {game.turn}] Player {game.current_player}")

            row = int(input("Row: "))
            col = int(input("Col: "))
            game.mark(row, col)

            print("\n")
            print(game.board)

            finished, winner = game.get_state()
            if finished:
                print("\n")

                if winner:
                    print(f"Player {winner} win!")
                else:
                    print(f"Draw!")

                break

            game.next_turn()

        except Exception as e:
            print("\n")
            print(e)
        finally:
            print("\n")


if __name__ == "__main__":
    main()
