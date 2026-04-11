from game import Board, Mark


def test_board_initialized_empty():
    board = Board(3, 3)
    for row in board.grid:
        for cell in row:
            assert cell is None


def test_board_str_empty():
    board = Board(3, 3)
    expected = "· · ·\n· · ·\n· · ·"
    assert str(board) == expected


def test_board_str_with_marks():
    board = Board(3, 3)
    board.mark(Mark.CIRCLE, 0, 0)
    board.mark(Mark.CROSS, 1, 1)
    expected = f"{Mark.CIRCLE} · ·\n· {Mark.CROSS} ·\n· · ·"
    assert str(board) == expected
