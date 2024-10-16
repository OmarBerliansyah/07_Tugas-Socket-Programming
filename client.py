import socket
import threading
import random 

def connect_server(server_ip,server_port):
    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    client.bind(("localhost",random.randint(8000,9000)))

    try: 
        client.sendto(b"PING", (server_ip,server_port))
        response,_ = client.recvfrom(1024)
        if response.decode() != "PONG":
            print("Tidak ada respons dari server")
            client.close()
            return None
        
    except (socket.error,socket.timeout):
        print("Unable to connect to the server")
        client.close 
        return None
    
    return client

while True:
    server_ip = input("Enter server IP (default: localhost): ") or "localhost"
    server_port = int(input("Enter server port (default: 9999): ") or 9999)
    
    try:
        server_port = int(server_port)
        client = connect_server(server_ip,server_port)
        if client:
            break
    except ValueError:
        print("Port invalid")

username = input("Masukkan Username: ")

# Penghandle-an password yang salah dan repetisi username
while True:
    password = input("Masukkan Password: ").strip()
    # Mengirimkan SIGNUP request ke server
    client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), (server_ip,server_port))
    
    # Menerima respons dari server
    response,_ = client.recvfrom(1024)
    response = response.decode()
    try:
        if response == "Password salah!":
            print("Password salah, silakan coba lagi.")
        elif response == "Username telah diambil!":
            print("Username sudah digunakan. coba username lain.")
            username = input("Masukkan username: ")
        elif response == "Berhasil bergabung ke chatroom!":
            print("Berhasil masuk ke chatroom.")
            break #keluar loop, signup client sukses
    except socket.error:
        print("""Koneksi terputus
              Keluar...""")
        client.close()
        exit(1)

# Fungsi untuk menerima dan memunculkan pesan dari server
def receive_message():
    while True:
        try:
            message,_ = client.recvfrom(1024)
            print(message.decode())
        except socket.error:
            print(f"Koneksi terputus karena {Exception}")
            break

# Menginisasi dan memulai thread receive message
t = threading.Thread(target = receive_message)
t.start()

# Mengirim permintaan sign up dengan username dan password

# Program untuk mengirim pesan (Loop)
while True:
    message = input()
    if message =="Aku nak keluar":
        print("Keluar dari chat room...")
        break
    else:
        client.sendto(message.encode(),(server_ip, server_port))
        print(f"")

client.close()