# Cara Run versi Dyah

1. Download semua file, yg kuubah si cuman nama folder test jadi tests, file main.py, file alice.py, bob.py, kdc.py, sama chat.py.
2. Buka CDM (Command Prompt) di laptop 1 trus cek ip nya pake ipconfig
3. Trus buka folder tugasnya
4. trus jalanin command buat kdc ini `python main.py kdc --host 192.168.1.2 --port 5000` ip nya sesuaikan
5. trus buka cdm di laptop 2, cek ip jg pake ipconfig
6. Trus buka folder, trus command buat alice yg ini `python main.py alice --kdc-host 192.168.1.2 --kdc-port 5000 --host 192.168.1.8 --port 5001` ip jangan lupa disesuaikan
7. trus lanjut ke terminal vm, mirip caranya cuman skrg command buat bob `python3 main.py bob --alice-host 192.168.1.8 --alice-port 5001` jangan lupa disesuaikan ip jg pake ip a ya di vm 
8. dah si skrg dah bisa chatan itu Bob sm Alice
9. ok bye dunia ak ngantok
10. good luck, jangan stres karena tugas kita dah oke mantap josjis

---

KDC + AES Manual (Tugas Keamanan Informasi)

Implementasi pembelajaran dengan:
- KDC, Alice, dan Bob sebagai tiga proses terpisah.
- AES-128 manual (bukan library AES siap pakai).
- Distribusi session key mengikuti pola lima langkah: Alice meminta key; KDC mengirim paket untuk Alice dan tiket Bob; Alice meneruskan tiket; Bob mengirim nonce; Alice mengembalikan nonce+1.
- Plaintext dan key dibatasi ke ASCII. Ciphertext ditampilkan/dikirim sebagai Hex.
- TCP dengan framing newline JSON.
- Test terpisah untuk AES dan fungsi encoding.

> Penting: cocokkan format pesan dan detail langkah 1–5 dengan PPT dosen. Implementasi ini memakai asumsi protokol yang dijelaskan di README; jika PPT berbeda, protokol harus disesuaikan.
> CBC tidak memberi autentikasi integritas. Ini proyek pembelajaran, bukan protokol untuk produksi.

## 1. Prasyarat
Python 3.10+ (tidak perlu menginstal library pihak ketiga).

## 2. Jalankan tes
```bash
python -m unittest discover -s tests -v
```

## 3. Pengujian awal pada satu laptop
Gunakan `127.0.0.1` untuk tes lokal. Buka tiga terminal di folder proyek.

Terminal 1 (kdc):
```
python main.py kdc --host 192.168.1.2 --port 5000
```
Masukkan key ASCII 16 karakter saat diminta, misalnya `AliceKey12345678` dan `BobKey1234567890`.

Terminal 2 (alice):
```
python main.py alice --kdc-host 192.168.1.2 --kdc-port 5000 --host 192.168.1.8 --port 5001
```
Masukkan K_A yang sama persis dengan KDC.

Terminal 3 (bob) (vm):
```
python3 main.py bob --alice-host 192.168.1.8 --alice-port 5001
```
Masukkan K_B yang sama persis dengan KDC.

Urutan: jalankan KDC, lalu Alice, lalu Bob. Setelah chat dimulai, ketik pesan di prompt `> `. Ketik `/rekey`, lalu masukkan key ASCII baru 16 karakter untuk memulai rotasi session key; tunggu konfirmasi sebelum mengirim pesan lagi. Ketik `/quit` untuk keluar.

## 4. Tiga perangkat
Cari IPv4 setiap perangkat dengan `ipconfig` (Windows) atau `ip addr` (Linux). Contoh alamat di bawah hanya ilustrasi:
- KDC: `192.168.1.10`
- Alice: `192.168.1.11`
- Bob: `192.168.1.12`

Terminal KDC:
```bash
python main.py kdc --host 0.0.0.0 --port 5000
```
KDC bind ke semua interface; Alice memakai IP LAN KDC untuk menghubunginya.

Terminal Alice:
```
python main.py alice --kdc-host 192.168.1.10 --kdc-port 5000 --host 0.0.0.0 --port 5001
```
Alice bind ke semua interface agar Bob bisa masuk. Gunakan IP LAN Alice sebagai tujuan Bob.

Terminal Bob:
```
python main.py bob --alice-host 192.168.1.11 --alice-port 5001
```
Sesuaikan IP aktual. Izinkan koneksi TCP pada port 5000 dan 5001 di firewall. Pastikan ketiga perangkat berada pada jaringan yang saling terjangkau.

## 5. Wireshark
Display filter:
```text
tcp.port == 5000 || tcp.port == 5001
```
Port 5000 adalah Alice–KDC; port 5001 adalah Alice–Bob. Payload JSON dan metadata masih terlihat, sedangkan paket yang dienkripsi muncul sebagai Hex.

## Batasan yang perlu dijelaskan
- KDC hanya melayani satu permintaan distribusi per proses; jalankan ulang KDC untuk sesi baru.
- AES-CBC tidak mengautentikasi ciphertext. Untuk keamanan nyata perlu MAC/AEAD dan protokol yang ditinjau ahli.
- Key yang dimasukkan harus 16 karakter ASCII (AES-128). Jangan menggunakan key contoh pada jaringan nyata.
- `/rekey` menyediakan pertukaran key dasar untuk demo. Ini protokol pembelajaran dan tidak aman untuk penggunaan produksi karena CBC tidak memberi autentikasi integritas; jika dosen meminta jaminan keamanan kuat, gunakan protokol yang diajarkan di kelas dan autentikasi pesan.
