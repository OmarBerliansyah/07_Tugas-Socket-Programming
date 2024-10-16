import socket
import threading


server_ip = "0.0.0.0"  # Accept connections from any network interface
server_port = 9999
PASSWORD = "MasihPemula"

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((server_ip,server_port))

clients = {}  # Menyimpan addr:username
username_set = set()  # Menyimpan semua username

# Fungsi untuk menerima pesan dari client
def receive_message():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            decoded = message.decode()

            if decoded == "PING":
                server.sendto("PONG".encode(),addr)
            elif "SIGNUP_TAG:" in decoded:
                _, uname, passwd = decoded.split(":")
                if passwd == PASSWORD:
                    if uname in username_set:
                        server.sendto("Username telah diambil!".encode(), addr)
                        print(f"Username {uname} sudah digunakan oleh client {addr}")
                    else:
                        username_set.add(uname)
                        clients[addr] = uname
                        server.sendto("Berhasil bergabung ke chatroom!".encode(), addr)
                        broadcast_message(f"{uname} telah bergabung ke chatroom!")
                        print(f"{uname} ({addr}) berhasil masuk ke chatroom.")
                else:
                    server.sendto("Password salah!".encode(), addr)
                    print(f"Client {addr} mencoba dengan password salah")
            else:
                uname = clients.get(addr, "Unknown")
                if decoded == "Aku nak keluar":
                    broadcast_message(f"{uname} telah meninggalkan chatroom.")
                    print(f"{uname} ({addr}) keluar dari chatroom.")
                    if addr in clients:
                        del clients[addr]
                        username_set.remove(uname)
                else:
                    broadcast_message(f"{uname}: {decoded}")
                    print(f"Pesan dari {uname}: {decoded}")

        except Exception as e:
            print(f"Error saat menerima pesan: {e}")

# Fungsi untuk broadcast pesan ke semua client
def broadcast_message(message):
    for client in clients:
        try:
            server.sendto(message.encode(), client)
        except Exception as e:
            print(f"Error saat mengirim pesan: {e}")

# Mulai thread untuk menerima pesan
t = threading.Thread(target=receive_message)
t.start()
