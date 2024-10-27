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

# Input username and password
username = input("Masukkan Username: ")
password = input("Masukkan Password: ")

# Send sign-up message with username and password to the server
client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), (address))

# Flag to stop receiving messages when exiting
stop_receive = False

# Function to receive messages from the server
def receive_message():
    while not stop_receive:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            
            # Handle server response on signup status
            if decoded_message == "Password salah!":
                print("Password salah, silakan coba lagi.")
                global stop_receive
                stop_receive = True  # Stop receiving after failed login
                client.close()
            elif decoded_message == "Username telah diambil!":
                print("Username sudah digunakan. coba username lain.")
                stop_receive = True
                client.close()
            elif decoded_message == "Berhasil bergabung ke chatroom!":
                print("Berhasil masuk ke chatroom.")
            else:
                print(decoded_message)  # Display other messages
        except Exception as e:
            if not stop_receive:
                print(f"Error saat menerima respon dari server: {e}")
            break

# Start a thread to handle incoming messages
t = threading.Thread(target=receive_message)
t.daemon = True  # Daemon thread to exit automatically with the main program
t.start()

# Main loop to send messages
while not stop_receive:
    message = input()
    
    if message == "Aku nak keluar":
        print("Keluar dari chat room...")
        client.sendto(message.encode(), (address))
        stop_receive = True
    else:
        try:
            client.sendto(message.encode(), (address))
        except Exception as e:
            print(f"Error saat mengirim pesan: {e}")

# Close the client socket and wait for receiving thread to finish
client.close()
t.join()