from game import Board, Marker


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
    board = Board(3)
    board.mark(Marker.O, 0, 0)
    board.mark(Marker.X, 1, 1)
    expected = f"{Marker.O} · ·\n· {Marker.X} ·\n· · ·"
    assert str(board) == expected


def test_mark_outside_bounds_raises_exception():
    board = Board(3)
    try:
        board.mark(Marker.O, 3, 0)
        assert False, "Expected exception"
    except Exception as e:
        assert "Cannot mark outside of board bounds" in str(e)


def test_mark_already_marked_raises_exception():
    board = Board(3)
    board.mark(Marker.O, 0, 0)
    try:
        board.mark(Marker.X, 0, 0)
        assert False, "Expected exception"
    except Exception as e:
        assert "already marked" in str(e)

def test_state_win_by_row_line():
    board = Board(3)
    board.mark(Marker.O, 0, 0)
    board.mark(Marker.O, 0, 1)
    board.mark(Marker.O, 0, 2)
    finished, winning_marker = board.check_state()
    assert finished and winning_marker == Marker.O
    
def test_state_win_by_column_line():
    board = Board(3)
    board.mark(Marker.X, 0, 0)
    board.mark(Marker.X, 1, 0)
    board.mark(Marker.X, 2, 0)
    finished, winning_marker = board.check_state()
    assert finished and winning_marker == Marker.X
    
def test_state_win_by_diagonal_line():
    board = Board(3)
    board.mark(Marker.X, 0, 0)
    board.mark(Marker.X, 1, 1)
    board.mark(Marker.X, 2, 2)
    finished, winning_marker = board.check_state()
    assert finished and winning_marker == Marker.X
    
def test_state_win_by_anti_diagonal_line():
    board = Board(3)
    board.mark(Marker.O, 0, 2)
    board.mark(Marker.O, 1, 1)
    board.mark(Marker.O, 2, 0)
    finished, winning_marker = board.check_state()
    assert finished and winning_marker == Marker.O
    
def test_state_unfinished():
    board = Board(3)
    board.mark(Marker.O, 0, 2)
    board.mark(Marker.O, 1, 1)
    finished, _ = board.check_state()
    assert not finished