import json
import threading
from aes.aes_cipher import encrypt_cbc, decrypt_cbc
from utils.encoding import require_aes128_key, ascii_bytes, to_hex, from_hex
from utils.network import send_json, recv_json

def run_chat(sock, role, session_key):
    # Receiver thread is the only reader from the socket. A lock protects
    # the active key while /rekey is being acknowledged.
    if isinstance(session_key, bytes):
        session_key = session_key.decode("ascii")

    state = {"key": require_aes128_key(session_key), "pending": None}
    lock = threading.Lock()
    stop = threading.Event()

    def active_key():
        with lock:
            return state["key"]

    def receiver():
        try:
            while not stop.is_set():
                obj = recv_json(sock)
                typ = obj.get("type")
                if typ == "quit":
                    print(f"\\n[{role}] Pihak lain menutup chat.")
                    stop.set()
                    break
                if typ == "chat":
                    plaintext = decrypt_cbc(active_key(), from_hex(obj["data"]))
                    print(f"\\n[{role} menerima] {plaintext.decode('ascii')}")
                    print("> ", end="", flush=True)
                elif typ == "rekey_offer":
                    old_key = active_key()
                    new_key = require_aes128_key(
                        decrypt_cbc(old_key, from_hex(obj["data"])).decode("ascii")
                    )
                    # Send acknowledgement under the OLD key, then activate new key.
                    send_json(sock, {"type":"rekey_ack",
                                     "data":to_hex(encrypt_cbc(old_key, b"ACK"))})
                    with lock:
                        state["key"] = new_key
                    print(f"\\n[{role}] Session key baru diterima dan diaktifkan.")
                    print("> ", end="", flush=True)
                elif typ == "rekey_ack":
                    old_key = active_key()
                    ack = decrypt_cbc(old_key, from_hex(obj["data"]))
                    if ack != b"ACK":
                        raise ValueError("Acknowledgement rekey tidak valid.")
                    with lock:
                        pending = state["pending"]
                        if pending is None:
                            raise ValueError("Acknowledgement rekey tidak diminta.")
                        state["key"] = pending
                        state["pending"] = None
                    print(f"\\n[{role}] Session key baru dikonfirmasi dan diaktifkan.")
                    print("> ", end="", flush=True)
                else:
                    print(f"\\n[{role}] Jenis pesan tidak dikenal: {typ}")
        except (ConnectionError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            if not stop.is_set():
                print(f"\\n[{role}] Penerimaan berhenti: {exc}")
            stop.set()

    thread = threading.Thread(target=receiver, daemon=True)
    thread.start()
    print(f"[{role}] Chat AES-CBC aktif.")
    print(f"[{role}] Perintah: /rekey (memasukkan key baru), /quit (keluar).")
    try:
        while not stop.is_set():
            try:
                line = input("> ")
            except EOFError:
                line = "/quit"
            if line.strip() == "/quit":
                try: send_json(sock, {"type":"quit"})
                except OSError: pass
                stop.set()
                break
            if line.strip() == "/rekey":
                try:
                    new_text = input("Key baru (16 karakter ASCII): ")
                    new_key = require_aes128_key(new_text)
                    old_key = active_key()
                    with lock:
                        if state["pending"] is not None:
                            print("[Rekey] Permintaan sebelumnya belum selesai.")
                            continue
                        state["pending"] = new_key
                    send_json(sock, {"type":"rekey_offer",
                                     "data":to_hex(encrypt_cbc(old_key, new_text.encode("ascii")))})
                    print("[Rekey] Penawaran dikirim; tunggu konfirmasi sebelum mengirim chat.")
                except (ValueError, OSError) as exc:
                    with lock:
                        state["pending"] = None
                    print(f"[Rekey] Gagal: {exc}")
                continue
            try:
                plain = ascii_bytes(line)
                payload = encrypt_cbc(active_key(), plain)
                send_json(sock, {"type":"chat", "data":to_hex(payload)})
            except (ValueError, OSError) as exc:
                print(f"[{role}] Pesan tidak terkirim: {exc}")
    finally:
        stop.set()
        try: sock.shutdown(2)
        except OSError: pass
        sock.close()
