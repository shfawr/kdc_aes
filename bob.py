import secrets
import socket
from aes.aes_cipher import encrypt_cbc, decrypt_cbc
from utils.encoding import require_aes128_key, parse_json_bytes, json_bytes, to_hex, from_hex
from utils.network import connect, send_json, recv_json
from chat import run_chat

def run_bob(alice_host, alice_port, kb_text):
    kb = require_aes128_key(kb_text)
    with connect(alice_host, alice_port, timeout=30) as conn:
        print(f"[Bob] Terhubung ke Alice di {alice_host}:{alice_port}.")
        msg = recv_json(conn)
        if msg.get("type") != "ticket":
            raise ValueError("Tiket dari Alice tidak ditemukan.")
        ticket = parse_json_bytes(decrypt_cbc(kb, from_hex(msg["ticket"])))
        if ticket.get("id_a") != "Alice" or ticket.get("id_b") != "Bob":
            raise ValueError("Identitas dalam tiket tidak valid.")
        sk_text = ticket.get("session_key", "")
        sk = require_aes128_key(sk_text)
        print("[Bob] Tiket berhasil dibuka; session key diperoleh.")
        n2 = str(secrets.randbelow(900000000) + 100000000)
        send_json(conn, {"type":"challenge", "data":to_hex(encrypt_cbc(sk, n2.encode("ascii")))})
        response = recv_json(conn)
        if response.get("type") != "challenge_response":
            raise ValueError("Respons challenge tidak ditemukan.")
        answer = decrypt_cbc(sk, from_hex(response["data"])).decode("ascii")
        if not answer.isdigit() or int(answer) != int(n2) + 1:
            send_json(conn, {"type":"verified", "ok":False})
            raise ValueError("Respons challenge salah.")
        send_json(conn, {"type":"verified", "ok":True})
        print("[Bob] Challenge-response berhasil; langkah 1-5 selesai.")
        conn.settimeout(None)
        run_chat(conn, "Bob", sk)
