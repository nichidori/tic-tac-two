from game import Game
from renderer import raw_mode, render, KEY


def main():
    # Initialize game
    game = Game()
    
    # Enter terminal raw mode, automatically restore on finish
    with raw_mode():
        # Current cursor position at [row, col]
        cursor = [0, 0] 
        
        while True:
            state = game.get_state()
            key = render(state, cursor)
            
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
                
                case KEY.EXIT:
                    break


if __name__ == "__main__":
    main()
