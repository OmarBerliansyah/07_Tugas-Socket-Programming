import socket
import threading

server_ip = "0.0.0.0"  # Accept connections from any network interface
server_port = 9999
PASSWORD = "MasihPemula"

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((server, server_port))

clients = {}  # Store addr:username
username_set = set()  # Store all usernames

# Function to receive messages from clients
def receive_message():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            decoded = message.decode()

            # Handle PING message
            if decoded == "PING":
                server.sendto("PONG".encode(), addr)

            # Handle user sign-up
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
                else:
                    server.sendto("Password salah!".encode(), addr)
                    print(f"Client {addr} attempted with wrong password")
            
            # Handle other messages
            else:
                uname = clients.get(addr, "Unknown")
                if decoded == "Aku nak keluar":
                    broadcast_message(f"{uname} telah meninggalkan chatroom.")
                    print(f"{uname} ({addr}) left the chatroom.")
                    if addr in clients:
                        del clients[addr]
                        username_set.remove(uname)
                else:
                    broadcast_message(f"{uname}: {decoded}")
                    print(f"Message from {uname}: {decoded}")

        except Exception as e:
            print(f"Error receiving message: {e}")

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client in clients:
        try:
            server.sendto(message.encode(), client)
        except Exception as e:
            print(f"Error sending message: {e}")

# Start thread to receive messages
t1 = threading.Thread(target=receive_message)
t2 = threading.Thread(target=broadcast_message)

t1.start()
t2.start()