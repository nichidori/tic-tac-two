from src.network import *


def test_payload_type_values():
    assert PayloadType.SET_PLAYER.value == 0
    assert PayloadType.MARK.value == 1
    assert PayloadType.EXIT.value == 2


def test_encode_decode_set_player():
    type = PayloadType.SET_PLAYER
    player_1 = True
    encoded = encode_payload(SetPlayerPayload(player_1))
    decoded_payload = decode_payload(type, encoded[3:])
    assert decoded_payload.type == type
    assert decoded_payload.player_1 == player_1


def test_encode_decode_set_player_false():
    type = PayloadType.SET_PLAYER
    player_1 = False
    encoded = encode_payload(SetPlayerPayload(player_1))
    decoded_payload = decode_payload(type, encoded[3:])
    assert decoded_payload.type == type
    assert decoded_payload.player_1 == player_1


def test_encode_decode_mark():
    type = PayloadType.MARK
    row, col = 1, 2
    encoded = encode_payload(MarkPayload(row, col))
    decoded_payload = decode_payload(type, encoded[3:])
    assert decoded_payload.type == type
    assert decoded_payload.row == row
    assert decoded_payload.col == col


def test_encode_decode_mark_zero():
    type = PayloadType.MARK
    row, col = 0, 0
    encoded = encode_payload(MarkPayload(row, col))
    decoded_payload = decode_payload(type, encoded[3:])
    assert decoded_payload.type == type
    assert decoded_payload.row == row
    assert decoded_payload.col == col


def test_encode_decode_exit():
    type = PayloadType.EXIT
    encoded = encode_payload(ExitPayload())
    decoded_payload = decode_payload(type, encoded[3:])
    assert decoded_payload.type == type
