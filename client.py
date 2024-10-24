import socket
import threading
import random

# Get server IP and port from user input (default values provided)
server_ip = input("Enter server IP (default: localhost): ") or "localhost"
server_port = int(input("Enter server port (default: 9999): ") or 9999)
address = (server_ip, server_port)

# Create the client socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('', random.randint(8000, 9000)))

# Input username
username = input("Masukkan Username: ")
password = input("Masukkan Password: ")
stop_receive = False

# Attempt sign-up with the server
while not stop_receive:
    
    try:
        response, _ = client.recvfrom(1024)
        response = response.decode()
        
        if response == "Password salah!":
            print("Password salah, silakan coba lagi.")
            client.close()
            break
        elif response == "Username telah diambil!":
            print("Username sudah digunakan. coba username lain.")
            client.close()
            break
        elif response == "Berhasil bergabung ke chatroom!":
            print("Berhasil masuk ke chatroom.")
            break
    except Exception as e:
        print(f"Error saat menerima respon dari server: {e}")
        break

# Function to receive messages from the server
def receive_message():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = (message.decode())
            print(decoded_message)
        except Exception as e:
            if not stop_receive:
                print(f"Error saat menerima pesan: {e}")
            break

# Start a thread to handle incoming messages
t = threading.Thread(target=receive_message)
t.daemon = True  # Daemon thread to exit automatically with the main program
t.start()

client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), (address))

# Main loop to send messages
while True:
    message = input()
    
    if message == "Aku nak keluar":
        print("Keluar dari chat room...")
        stop_receive = True
        break
    else:
        try:
            client.sendto(message.encode(), (address))
        except Exception as e:
            print(f"Error saat mengirim pesan: {e}")

# Close the client socket before exiting
client.close()
t.join()