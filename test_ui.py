from src.ui import (
    Key,
    handle_main_menu_input,
    handle_server_starting_input,
    handle_client_starting_input,
    handle_game_input,
)
from src.game import Game, Pos


def test_handle_main_menu_input_1():
    assert handle_main_menu_input("1") == Key.START_SERVER


def test_handle_main_menu_input_2():
    assert handle_main_menu_input("2") == Key.START_CLIENT


def test_handle_main_menu_input_q():
    assert handle_main_menu_input("q") == Key.EXIT


def test_handle_main_menu_input_ctrl_c():
    assert handle_main_menu_input("\x03") == Key.EXIT


def test_handle_main_menu_input_invalid():
    assert handle_main_menu_input("x") is None


def test_handle_server_starting_input_ctrl_c():
    assert handle_server_starting_input("\x03") == Key.EXIT


def test_handle_server_starting_input_other():
    assert handle_server_starting_input("a") is None


def test_handle_client_starting_input_enter():
    assert handle_client_starting_input("\r") == Key.SELECT


def test_handle_client_starting_input_delete():
    assert handle_client_starting_input("\x7f") == Key.DELETE


def test_handle_client_starting_input_ctrl_c():
    assert handle_client_starting_input("\x03") == Key.EXIT


def test_handle_client_starting_input_digit():
    assert handle_client_starting_input("1") == "1"
    assert handle_client_starting_input("9") == "9"


def test_handle_client_starting_input_dot():
    assert handle_client_starting_input(".") == "."

    assert handle_client_starting_input("a") is None


def test_handle_game_input_arrow_up():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\x1b[A", game, cursor_pos) == Key.CURSOR_UP


def test_handle_game_input_arrow_down():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\x1b[B", game, cursor_pos) == Key.CURSOR_DOWN


def test_handle_game_input_arrow_left():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\x1b[D", game, cursor_pos) == Key.CURSOR_LEFT


def test_handle_game_input_arrow_right():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\x1b[C", game, cursor_pos) == Key.CURSOR_RIGHT


def test_handle_game_input_w():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("w", game, cursor_pos) == Key.CURSOR_UP


def test_handle_game_input_s():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("s", game, cursor_pos) == Key.CURSOR_DOWN


def test_handle_game_input_a():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("a", game, cursor_pos) == Key.CURSOR_LEFT


def test_handle_game_input_d():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("d", game, cursor_pos) == Key.CURSOR_RIGHT


def test_handle_game_input_enter():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\r", game, cursor_pos) == Key.SELECT


def test_handle_game_input_ctrl_c():
    game = Game()
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\x03", game, cursor_pos) == Key.EXIT


def test_handle_game_input_prevents_already_marked():
    game = Game()
    game.mark(Pos(1, 1))
    cursor_pos = Pos(1, 1)
    assert handle_game_input("\r", game, cursor_pos) is None


def test_handle_game_input_prevents_cursor_at_top():
    game = Game()
    cursor_pos = Pos(0, 1)
    assert handle_game_input("\x1b[A", game, cursor_pos) is None
    assert handle_game_input("w", game, cursor_pos) is None


def test_handle_game_input_prevents_cursor_at_bottom():
    game = Game()
    cursor_pos = Pos(2, 1)
    assert handle_game_input("\x1b[B", game, cursor_pos) is None
    assert handle_game_input("s", game, cursor_pos) is None


def test_handle_game_input_prevents_cursor_at_left():
    game = Game()
    cursor_pos = Pos(1, 0)
    assert handle_game_input("\x1b[D", game, cursor_pos) is None
    assert handle_game_input("a", game, cursor_pos) is None


def test_handle_game_input_prevents_cursor_at_right():
    game = Game()
    cursor_pos = Pos(1, 2)
    assert handle_game_input("\x1b[C", game, cursor_pos) is None
    assert handle_game_input("d", game, cursor_pos) is None
