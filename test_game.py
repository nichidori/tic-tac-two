from game import Board, Game, Marker


def test_board_initialized_empty():
    board = Board(3)
    for row in board.grid:
        for cell in row:
            assert cell is None


def test_board_str_empty():
    board = Board(3)
    expected = "· · ·\n· · ·\n· · ·"
    assert str(board) == expected


def test_board_str_with_marks():
    game = Game()
    game.mark(0, 0)  # Player 1 = O
    game.next_turn()
    game.mark(1, 1)  # Player 2 = X
    expected = f"{Marker.O} · ·\n· {Marker.X} ·\n· · ·"
    assert str(game.board) == expected


def test_mark_outside_bounds_raises_exception():
    game = Game()
    try:
        game.mark(3, 0)
        assert False, "Expected exception"
    except Exception as e:
        assert "Cannot mark outside of board bounds" in str(e)


def test_mark_already_marked_raises_exception():
    game = Game()
    game.mark(0, 0)
    try:
        game.mark(0, 0)
        assert False, "Expected exception"
    except Exception as e:
        assert "Cell is already marked" in str(e)


def test_state_win_by_row():
    game = Game()
    game.board.grid[0] = [Marker.O, Marker.O, Marker.O]
    finished, winner = game.get_state()
    assert finished and winner == 1


def test_state_win_by_column():
    game = Game()
    for row in range(3):
        game.board.grid[row][0] = Marker.X
    finished, winner = game.get_state()
    assert finished and winner == 2


def test_state_win_by_main_diagonal():
    game = Game()
    for i in range(3):
        game.board.grid[i][i] = Marker.O
    finished, winner = game.get_state()
    assert finished and winner == 1


def test_state_win_by_anti_diagonal():
    game = Game()
    for i in range(3):
        game.board.grid[i][2 - i] = Marker.X
    finished, winner = game.get_state()
    assert finished and winner == 2


def test_state_draw():
    game = Game()
    game.board.grid = [
        [Marker.O, Marker.X, Marker.O],
        [Marker.O, Marker.X, Marker.X],
        [Marker.X, Marker.O, Marker.O],
    ]
    finished, winner = game.get_state()
    assert finished and winner is None


def test_state_unfinished():
    game = Game()
    game.mark(0, 0)
    finished, _ = game.get_state()
    assert not finished
