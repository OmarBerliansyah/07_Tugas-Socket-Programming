import socket
import threading
import queue
from datetime import datetime

PASSWORD = "MasihPemula"
broadcast_port = 8888  # Port untuk mendengar input server_port dari client

# Membuat socket UDP untuk menerima input server_port
port_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port_listener.bind(('', broadcast_port)) #IP address untuk koneksi dibuat untuk menyesuaikan 

# Menunggu client melakukan broadcast dari port yang di-input
print("Menunggu client untuk melakukan broadcast di port yang dituju...")
message, addr = port_listener.recvfrom(1024) #Menghubungkan ke port untuk mendengar pesan
server_port = int(message.decode())
print(f"Mengatur port server menjadi {server_port} sebagai tempat menerima pesan .")
port_listener.close()

server_ip = socket.gethostbyname(socket.gethostname())
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((server_ip, server_port))

#Struktur data untuk menyimpan data client, username, pesan, dan history chat
clients = {} 
username_set = set()
messages = queue.Queue()
chat_history_by_users = {}

LOG_FILE = "chat_history.txt" #inisiasi file untuk menyimpan history chat

# Fungsi untuk mendapatkan timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Fungsi untuk menyimpan pesan ke file berdasarkan pengguna, dengan timestamp
def save_message(user_pair, message):
    timestamp = get_timestamp()  # Dapatkan timestamp
    full_message = f"[{timestamp}] {message}"
    print(f"Saving message: {full_message}")
    
    # Menyimpan semua pesan terkirim di dalam dictionary history pesan pada key "Chatroom"
    if "Chatroom" not in chat_history_by_users:
        chat_history_by_users["Chatroom"] = []
    chat_history_by_users["Chatroom"].append(full_message)
    
    # Menyimpan pesan terkirim ke file .txt
    with open(LOG_FILE, "a") as file:
        file.write(f"{full_message}\n")

# Fungsi untuk membaca riwayat pesan dari file berdasarkan pengguna
def load_messages():
    try:
        with open(LOG_FILE, "r") as file:
            lines = file.readlines()
            return [line.strip() for line in lines]
    except FileNotFoundError:
        return []
# Fungsi untuk mengirimkan pesan dari pengirim ke alamat client yang dituju 
def broadcast_message(message, sender_addr=None):
    for client_addr in clients.keys():
        if client_addr != sender_addr:
            try:
                server.sendto(message.encode(), client_addr)
            except Exception as e:
                print(f"Error saat mengirim pesan ke client {client_addr}: {e}")

# Fungsi untuk melakukan handshake antara server dan client
def perform_handshake(addr):
    print(f"Received SYN from {addr}. Sending SYN-ACK...")
    server.settimeout(3)  # Timeout ACK \\ ACK tidak berhasil

    try:
        server.sendto("SYN-ACK".encode(), addr)
        ack, _ = server.recvfrom(1024)
        if ack.decode() == "ACK":
            print(f"Handshake dengan {addr} berhasil.")
            return True
    except socket.timeout:
        print(f"Handshake dengan {addr} gagal: Tidak ada ACK.")
        print("Kemungkinan penyebab:")
        print("- Koneksi klient mungkin terputus sebelum selesai handshake.")
        print("- Permasalahan jaringan yang menyebabkan packet loss.")
    finally:
        server.settimeout(None)  # Menghentikan timeout setelah upaya handshake selesai

    return False

def rc4(key, data):
    # Menginisiasi array S dengan key-scheduling algorithm (KSA)
    S = list(range(256))
    j = 0
    key = [ord(c) for c in key]
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    # Pseudo-random generation algorithm (PRGA) 
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
    while True:
        try:
            message, addr = server.recvfrom(1024)
            decoded = message.decode()
            decrypt = rc4(ENCRYPT_KEY, decoded)
            
            if decoded == "SYN":
                if not perform_handshake(addr):
                    print("Failed to complete handshake. Connection refused.")
                    continue
            
            elif "SIGNUP_TAG:" in decoded:
                _, uname, passwd = decoded.split(":")
                if passwd == PASSWORD:
                    if uname in username_set:
                        server.sendto("Username telah diambil!".encode(), addr)
                        print(f"Username {uname} already in use by client {addr}")
                    else:
                        username_set.add(uname)
                        clients[addr] = uname
                        server.sendto("Berhasil bergabung ke chatroom!".encode(), addr)
                        broadcast_message(f"{uname} telah bergabung ke chatroom!")
                        print(f"{uname} ({addr}) successfully joined the chatroom.")

                        # Memroses dan mengirim seluruh history dari chat room 
                        past_messages = load_messages()
                        for past_message in past_messages:
                            server.sendto(past_message.encode(), addr)
                        print(f"Sent chat history to {uname} ({addr}).")
                else:
                    server.sendto("Password salah!".encode(), addr)
                    print(f"Client {addr} attempted with wrong password")

            elif addr in clients:
                uname = clients.get(addr, "Unknown")
                if decoded == "Aku nak keluar":
                    broadcast_message(f"{uname} telah meninggalkan chatroom.")
                    print(f"{uname} ({addr}) meninggalkan chatroom.")
                    if addr in clients:
                        del clients[addr]
                        username_set.remove(uname)
                else:
                    broadcast_message(f"{uname}: {decrypt}", sender_addr=addr)
                    save_message("Chatroom", f"{uname}: {decrypt}")
                    print(f"Message from {uname}: {decrypt}")
                    server.sendto("ACK".encode(), addr)
                    
        except ConnectionResetError:
            # Menghandle apabila koneksi dengan client tiba-tiba terputus
            if addr in clients:
                uname = clients.pop(addr)
                username_set.remove(uname)
                print(f"Koneksi dengan client {addr} ({uname}) terputus.")
                broadcast_message(f"{uname} telah terputus dengan chatroom.")
        except KeyboardInterrupt:
            print("Server interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"Error saat menerima pesan: {e}")

t1 = threading.Thread(target=receive_message)
t1.daemon = True
t1.start()

try:
    t1.join()
except KeyboardInterrupt:
    print("Mematikan server.")
finally:
    server.close()