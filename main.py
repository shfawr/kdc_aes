import argparse
from getpass import getpass
from kdc import run_kdc
from alice import run_alice
from bob import run_bob
from test.test_aes import run_aes_self_test

def read_key(label):
    while True:
        key = getpass(f"Masukkan {label} (tepat 16 karakter ASCII): ")
        try:
            raw = key.encode("ascii")
        except UnicodeEncodeError:
            print("Key harus ASCII.")
            continue
        if len(raw) != 16:
            print("Key harus tepat 16 byte/karakter ASCII.")
            continue
        return key

def main():
    parser = argparse.ArgumentParser(description="KDC + AES-128 manual")
    sub = parser.add_subparsers(dest="role", required=True)

    sub.add_parser("test", help="Jalankan self-test AES")

    p = sub.add_parser("kdc", help="Jalankan KDC")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)

    p = sub.add_parser("alice", help="Jalankan Alice")
    p.add_argument("--kdc-host", default="127.0.0.1")
    p.add_argument("--kdc-port", type=int, default=5000)
    p.add_argument("--host", default="127.0.0.1", help="Alamat bind server Alice")
    p.add_argument("--port", type=int, default=5001)

    p = sub.add_parser("bob", help="Jalankan Bob")
    p.add_argument("--alice-host", default="127.0.0.1")
    p.add_argument("--alice-port", type=int, default=5001)

    args = parser.parse_args()
    if args.role == "test":
        run_aes_self_test()
    elif args.role == "kdc":
        ka = read_key("K_A (rahasia KDC-Alice)")
        kb = read_key("K_B (rahasia KDC-Bob)")
        run_kdc(args.host, args.port, ka, kb)
    elif args.role == "alice":
        ka = read_key("K_A (harus sama dengan key di KDC)")
        run_alice(args.kdc_host, args.kdc_port, args.host, args.port, ka)
    elif args.role == "bob":
        kb = read_key("K_B (harus sama dengan key di KDC)")
        run_bob(args.alice_host, args.alice_port, kb)

if __name__ == "__main__":
    main()
