import secrets
import socket
from aes.aes_cipher import encrypt_cbc
from utils.encoding import require_aes128_key, json_bytes, to_hex
from utils.network import send_json, recv_json

def run_kdc(host, port, ka_text, kb_text):
    ka, kb = require_aes128_key(ka_text), require_aes128_key(kb_text)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        print(f"[KDC] Listening on {host}:{port}; menunggu satu permintaan.")
        conn, addr = server.accept()
        with conn:
            conn.settimeout(15)
            try:
                req = recv_json(conn)
                if req.get("type") != "request" or req.get("id_a") != "Alice" or req.get("id_b") != "Bob":
                    raise ValueError("Format/identitas permintaan tidak valid.")
                n1 = req.get("n1")
                if not isinstance(n1, str) or not n1:
                    raise ValueError("Nonce Alice tidak valid.")
                session_key = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(16))
                ticket = {"id_a":"Alice", "id_b":"Bob", "session_key":session_key, "n1":n1}
                for_alice = {"id_a":"Alice", "id_b":"Bob", "session_key":session_key, "n1":n1}
                response = {
                    "type":"kdc_response",
                    "alice_packet":to_hex(encrypt_cbc(ka, json_bytes(for_alice))),
                    "bob_ticket":to_hex(encrypt_cbc(kb, json_bytes(ticket)))
                }
                send_json(conn, response)
                print("[KDC] Permintaan diterima; paket Alice dan tiket Bob dikirim.")
                print("[KDC] Session key dibuat (nilainya tidak ditampilkan).")
            except Exception as exc:
                print(f"[KDC] Permintaan gagal: {exc}")
                raise
        print("[KDC] Sesi distribusi selesai. Jalankan ulang KDC untuk sesi baru.")
