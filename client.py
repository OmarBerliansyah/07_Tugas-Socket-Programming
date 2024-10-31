import socket
import threading
import random

# Input desired server port
server_port = int(input("Enter server port for chat room (e.g., 9999): "))
broadcast_address = ('<broadcast>', 8888)

# Create a UDP socket for broadcasting the desired port
client_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client_broadcast.sendto(str(server_port).encode(), broadcast_address)
client_broadcast.close()

# Now, connect to the server on the desired port
server_ip = input("Enter server IP (default: localhost): ") or "localhost"
address = (server_ip, server_port)

stop_receive = False

def receive_message():
    global stop_receive
    while not stop_receive:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except socket.error as e:
            if not stop_receive:
                print(f"Error receiving from server: {e}")
                break

logged_in = False
while not logged_in:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('', random.randint(8000, 9000)))
    username = input("Enter Username: ")
    while True:
        password = input("Enter Password: ")
        client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), address)
        message, _ = client.recvfrom(1024)
        decoded_message = message.decode()
        if decoded_message == "Password salah!":
            print("Wrong password, try again.")
            continue
        elif decoded_message == "Username telah diambil!":
            print("Username already taken. Try another.")
            break
        elif decoded_message == "Berhasil bergabung ke chatroom!":
            print("Successfully joined the chat room.")
            logged_in = True
            break

t = threading.Thread(target=receive_message)
t.daemon = True
t.start()

while not stop_receive:
    message = input()
    if message == "Aku nak keluar":
        print("Leaving chat room...")
        client.sendto(message.encode(), address)
        stop_receive = True
    else:
        client.sendto(message.encode(), address)

client.close()
t.join()
