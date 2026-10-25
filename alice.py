import secrets
import socket
from aes.aes_cipher import encrypt_cbc, decrypt_cbc
from utils.encoding import require_aes128_key, json_bytes, parse_json_bytes, to_hex, from_hex
from utils.network import connect, send_json, recv_json
from chat import run_chat

def run_alice(kdc_host, kdc_port, host, port, ka_text):
    ka = require_aes128_key(ka_text)
    n1 = str(secrets.randbelow(900000000) + 100000000)
    # Buka listener lebih dulu agar Bob dapat terhubung setelah menerima tiket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(1)
        listener.settimeout(30)
        print(f"[Alice] Menunggu Bob pada {host}:{port} (listener siap).")
        with connect(kdc_host, kdc_port) as kdc:
            send_json(kdc, {"type":"request", "id_a":"Alice", "id_b":"Bob", "n1":n1})
            response = recv_json(kdc)
        if response.get("type") != "kdc_response":
            raise ValueError("Respons KDC tidak dikenal.")
        packet = parse_json_bytes(decrypt_cbc(ka, from_hex(response["alice_packet"])))
        if packet.get("id_a") != "Alice" or packet.get("id_b") != "Bob" or packet.get("n1") != n1:
            raise ValueError("Respons KDC atau nonce tidak cocok.")
        session_key = packet.get("session_key", "")
        sk = require_aes128_key(session_key)
        print("[Alice] Respons KDC dan nonce terverifikasi.")
        print("[Alice] Menunggu Bob menghubungkan diri...")
        conn, addr = listener.accept()
        with conn:
            conn.settimeout(30)
            print(f"[Alice] Bob terhubung dari {addr[0]}:{addr[1]}.")
            send_json(conn, {"type":"ticket", "ticket":response["bob_ticket"]})
            challenge = recv_json(conn)
            if challenge.get("type") != "challenge":
                raise ValueError("Challenge Bob tidak valid.")
            n2_enc = from_hex(challenge["data"])
            n2 = decrypt_cbc(sk, n2_enc).decode("ascii")
            if not n2.isdigit():
                raise ValueError("Nonce Bob tidak valid.")
            answer = str(int(n2) + 1)
            send_json(conn, {"type":"challenge_response", "data":to_hex(encrypt_cbc(sk, answer.encode("ascii")))})
            result = recv_json(conn)
            if result.get("type") != "verified" or result.get("ok") is not True:
                raise ValueError("Bob menolak respons challenge.")
            print("[Alice] Langkah 1-5 selesai; challenge-response berhasil.")
            conn.settimeout(None)
            run_chat(conn, "Alice", sk)
