import json
import socket

MAX_LINE = 1_000_000

def send_json(sock: socket.socket, obj: dict) -> None:
    data = json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
    sock.sendall(data)

def recv_json(sock: socket.socket) -> dict:
    # TCP adalah stream; baca sampai newline agar satu pesan lengkap diterima.
    chunks = bytearray()
    while True:
        part = sock.recv(1)
        if not part:
            raise ConnectionError("Koneksi ditutup sebelum pesan lengkap diterima.")
        if part == b"\n":
            break
        chunks.extend(part)
        if len(chunks) > MAX_LINE:
            raise ValueError("Pesan jaringan terlalu besar.")
    return json.loads(chunks.decode("ascii"))

def connect(host: str, port: int, timeout: float = 10.0) -> socket.socket:
    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    return sock
