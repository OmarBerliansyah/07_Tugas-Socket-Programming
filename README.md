# II2120-Jarkom
# Tugas Besar 1 Jaringan Komputer - Kelas K01

*Kelompok: MasihPemula*  

---

## Deskripsi
*  Program chatroom sederhana ini menggunakan protokol UDP sebagai cara mentransport pesan, pengguna/client-side cukup memasukkan
*  server dan port yang akan dituju, lalu dari server-side akan menghandle input tersebut dan setelah terkoneksi, server akan mendengar
*  pesan yang dikirim oleh pengguna dan ditampilkan di terminal

## Anggota Kelompok
- **Raka Aditya Nugraha** - *18223013*
- **Muhammad Omar Berliansyah** - *18223055*

## Fitur
*  1. Mampu menerima input dan output port dari client dan mengalokasikan port untuk digunakan.
*  2. Setiap client memiliki username yang unik dan memerlukan password untuk masuk ke chatroom.
*  3. Menggunakan fitur TCP over UDP sehingga menjamin koneksi client dan server.
*  4. Menggunakan enkripsi pesan RC4 sebelum mengirimkan pesan antar client.
*  5. Memiliki history chat setiap server, sehingga selama server tidak mati, chat yang lalu akan dapat dilihat kembali.

## Cara Menggunakan
*  1. Mendownload source code pada laman github ini dan menyimpannya sebagai server.py dan client.py.
*  2. Menjalankan program server.py pada dengan compiler python pada IDE masing-masing atau pada terminal dengan mengarahkan directory folder ke folder tempat server.py, lalu memasukkan "python server.py" pada terminal.
*  3. Buka terminal atau command prompt dan arahkan directorynya ke folder yang mengandung file client.py, .
*  4. Jalankan client.py dengan compiler python atau menginput "python client.py" pada terminal 
*  5. Masukkan IP dan Port yang ingin dituju (Pastikan jaringan internet anda sama dengan jaringan server, cara mengecek adalah dengan mengetik ipconfig pada terminal dan cari kolom IPv4 dari Wireless LAN Adapter Wi-Fi)
*  6. Login: Masukkan username yang akan dipakai di chatroom, harus unik, tidak boleh sama dengan yang pernah login di chatroom.
*  7. Masukkan password, yang memegang password adalah pemilik server sehingga bisa menghubungi yang bersangkutan atau mengecek di source code server.
*  8. Jika proses ACK telah berhasil, pengguna sudah terhubung ke chatroom dan bisa memulai untuk mengirim teks pesan.
*  9. Jika ingin menambah jumlah client pada chatroom, bisa membuka terminal baru pada device dengan jaringan yang sama dan mengulangi langkah 3 s.d. 7.
*  10. Jika ingin keluar dari chatroom, kirim pesan "Aku nak keluar" dan program client.py akan berakhir.
