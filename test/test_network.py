from src.network import PayloadType, encode_payload, decode_payload


def test_payload_type_values():
    assert PayloadType.SET_PLAYER.value == 0
    assert PayloadType.MARK.value == 1
    assert PayloadType.EXIT.value == 2


def test_encode_decode_set_player():
    type = PayloadType.SET_PLAYER
    player_1 = True
    encoded = encode_payload(type, player_1)
    decoded_type, decoded_data = decode_payload(type, encoded[3:])
    assert decoded_type == PayloadType.SET_PLAYER
    assert decoded_data == player_1


def test_encode_decode_set_player_false():
    type = PayloadType.SET_PLAYER
    player_1 = False
    encoded = encode_payload(type, player_1)
    decoded_type, decoded_data = decode_payload(type, encoded[3:])
    assert decoded_type == PayloadType.SET_PLAYER
    assert decoded_data == player_1


def test_encode_decode_mark():
    type = PayloadType.MARK
    row, col = 1, 2
    encoded = encode_payload(type, row, col)
    decoded_type, decoded_data = decode_payload(type, encoded[3:])
    assert decoded_type == PayloadType.MARK
    assert decoded_data == (row, col)


def test_encode_decode_mark_zero():
    type = PayloadType.MARK
    row, col = 0, 0
    encoded = encode_payload(type, row, col)
    decoded_type, decoded_data = decode_payload(type, encoded[3:])
    assert decoded_type == PayloadType.MARK
    assert decoded_data == (row, col)


def test_encode_decode_exit():
    type = PayloadType.EXIT
    encoded = encode_payload(type)
    decoded_type, decoded_data = decode_payload(type, encoded[3:])
    assert decoded_type == PayloadType.EXIT
    assert decoded_data is None
