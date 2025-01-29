import socket
import threading
import random


# Client bisa menginput port dan IP yang diinginkan 
server_port = int(input("Masukkan port untuk chat room (e.g., 9999): "))
broadcast_address = ('<broadcast>', 8888)

# Membuat socket UDP berdasarkan input IP dan port client
client_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client_broadcast.sendto(str(server_port).encode(), broadcast_address)
client_broadcast.close()

# Menghubungkan client ke server melalui IP dan port yang dituju
server_ip = input("Masukkan IP server (default: localhost): ") or "localhost"
address = (server_ip, server_port)

stop_receive = False

def rc4(key, data):
    S = list(range(256))
    j = 0
    key = [ord(c) for c in key]
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    i = j = 0
    result = []
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        result.append(chr(ord(char) ^ K))
    
    return ''.join(result)

ENCRYPT_KEY = "AkuMahMasihPemulaPuh"

def receive_message():
    global stop_receive
    while not stop_receive:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            if decoded_message == "ACK":
                print("Server menerima pesan.")
            else:
                print(decoded_message)
        except socket.error as e:
            if not stop_receive:
                print(f"Error saat menerima dari server: {e}")
                break

def initiate_handshake():
    print("Memulai handshake...")
    attempts = 3  # Banyaknya upaya handshake jika tidak langsung berhasil
    client.settimeout(3)  # Timeout atau jeda sesaat setelah setiap upaya handshake

    for attempt in range(1, attempts + 1):
        try:
            print(f"Percobaan handshake ke-{attempt} dari {attempts}")
            client.sendto("SYN".encode(), address)
            response, _ = client.recvfrom(1024)
            
            if response.decode() == "SYN-ACK":
                print("Menerima SYN-ACK, mengirim ACK untuk menyelesaikan handshake.")
                client.sendto("ACK".encode(), address)
                client.settimeout(None)  
                print("Handshake telah berhasil.")
                return True
        except socket.timeout:
            print(f"Percobaan {attempt} gagal: tidak ada respons dari server. Menghubungkan kembali...")
        except ConnectionResetError:
            print("Koneksi ditutup secara paksa oleh remote host. Coba untuk meninjau hal-hal berikut:")
            print("- Port server mungkin salah atau tidak bisa terkoneksi.")
            print("- Server mungkin sedang offline atau tidak mendengarkan port tersebut.")
            return False
        except socket.error as e:
            print(f"Error tak terduga pada socket : {e}")
            return False
    
    # Handshake sudah mencapai nilai maksimum
    print("Handshake gagal setelah percobaan maksimal. Kemungkinan alasannya adalah:")
    print("- Server sedang offline atau tidak bisa terkoneksi.")
    print("- IP dan port yang salah.")
    print("- Packet loss akibat masalah jaringan.")
    return False

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('', random.randint(8000, 9000)))

# Melakukan handshake, keluar program jika gagal
if not initiate_handshake():
    client.close()
    exit()

logged_in = False
while not logged_in:
    username = input("Masukkan username: ")
    while True:
        password = input("Masukkan Password: ")
        client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), address)
        message, _ = client.recvfrom(1024)
        decoded_message = message.decode()
        if decoded_message == "Password salah!":
            print("Password salah! silakan coba lagi.")
            continue
        elif decoded_message == "Username telah diambil!":
            print("Username telah diambil! silakan input username yang unik.")
            break
        elif decoded_message == "Berhasil bergabung ke chatroom!":
            print("Berhasil bergabung ke chatroom!")
            logged_in = True
            break

# Mulai untuk menerima pesan pada thread yang terpisah
t = threading.Thread(target=receive_message)
t.daemon = True
t.start()

try:
    while not stop_receive:
        message = input()
        encrypt = rc4(ENCRYPT_KEY, message)
        if message == "Aku nak keluar":
            print("Meninggalkan chat room...")
            client.sendto(message.encode(), address)
            stop_receive = True
        else:
            client.sendto(encrypt.encode(), address)
except KeyboardInterrupt:
    print("Client menginterupsi. Keluar program...")
finally:
    stop_receive = True
    client.close()
    t.join()
