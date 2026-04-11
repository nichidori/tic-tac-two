from game import Board


def test_board_initialized_empty():
    board = Board(3, 3)
    for row in board.grid:
        for cell in row:
            assert cell is None


def test_board_str_empty():
    board = Board(3, 3)
    expected = "· · ·\n· · ·\n· · ·\n"
    assert str(board) == expected


def test_board_str_with_mark():
    board = Board(3, 3)
    board.grid[1][1] = "X"
    expected = "· · ·\n· X ·\n· · ·\n"
    assert str(board) == expected
