import socket

from enum import Enum


PORT = 41034


def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server.bind(("0.0.0.0", PORT))
        server.listen(1)
        return server
    except Exception:
        server.close()
        return None


def connect_server(server_ip="127.0.0.1"):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, PORT))
        return sock
    except Exception:
        sock.close()
        return None


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("10.255.255.255", 1))
        ip = sock.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        sock.close()
    return ip


class PayloadType(Enum):
    SET_PLAYER = 0
    MARK = 1
    EXIT = 2


class Payload:
    def __init__(self, type):
        self.type = type


class SetPlayerPayload(Payload):
    def __init__(self, player_1):
        super().__init__(PayloadType.SET_PLAYER)
        self.player_1 = player_1


class MarkPayload(Payload):
    def __init__(self, row, col):
        super().__init__(PayloadType.MARK)
        self.row = row
        self.col = col


class ExitPayload(Payload):
    def __init__(self):
        super().__init__(PayloadType.EXIT)


def send_payload(socket, payload):
    payload = encode_payload(payload)
    socket.sendall(payload)


def receive_payload(socket):
    header_bytes = socket.recv(3)

    if not header_bytes or len(header_bytes) < 3:
        return None

    type = PayloadType(int.from_bytes(header_bytes[:1]))
    data_len = int.from_bytes(header_bytes[1:3])

    data_bytes = socket.recv(data_len)

    if not data_bytes or len(data_bytes) < data_len:
        return None

    return decode_payload(type, data_bytes)


def encode_payload(payload):
    type_bytes = payload.type.value.to_bytes(1)

    match payload:
        case SetPlayerPayload():
            player_1 = int(payload.player_1).to_bytes(1)
            data_bytes = player_1

        case MarkPayload():
            row = payload.row.to_bytes(4)
            col = payload.col.to_bytes(4)
            data_bytes = row + col

        case ExitPayload():
            data_bytes = bytes(1)

    len_bytes = len(data_bytes).to_bytes(2)
    return type_bytes + len_bytes + data_bytes


def decode_payload(type, data_bytes):
    match type:
        case PayloadType.SET_PLAYER:
            player_1 = data_bytes[0] == 1
            return SetPlayerPayload(player_1)

        case PayloadType.MARK:
            row = int.from_bytes(data_bytes[0:4])
            col = int.from_bytes(data_bytes[4:8])
            return MarkPayload(row, col)

        case PayloadType.EXIT:
            return ExitPayload()
