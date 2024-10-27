import socket
import threading
import random

# Get server IP and port from user input (default values provided)
server_ip = input("Enter server IP (default: localhost): ") or "localhost"
server_port = int(input("Enter server port (default: 9999): ") or 9999)
address = (server_ip, server_port)

# Flag to stop receiving messages when exiting
stop_receive = False

# Function to handle receiving messages from server
def receive_message():
    global stop_receive
    while not stop_receive:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            print(decoded_message)  # Display incoming message

            # Stop receiving if the client is instructed to exit
            if "Password salah" in decoded_message or "Username telah diambil" in decoded_message:
                stop_receive = True  # Signal to stop receiving on login failure

        except Exception as e:
            if not stop_receive:
                print(f"Error saat menerima respon dari server: {e}")
            break

# Loop until successful login
logged_in = False

while not logged_in:
    # Create a new client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('', random.randint(8000, 9000)))

    # Prompt for username
    username = input("Masukkan Username: ")

    # Loop to prompt for password until successful login
    while True:
        password = input("Masukkan Password: ")
        # Send sign-up message with username and password to the server
        client.sendto(f"SIGNUP_TAG:{username}:{password}".encode(), (address))

        # Receive response from server to check login status
        message, _ = client.recvfrom(1024)
        decoded_message = message.decode()

        # Check server response
        if decoded_message == "Password salah!":
            print("Password salah, silakan coba lagi.")
            # Prompt for password again
            continue  # Loop back to prompt for password
        elif decoded_message == "Username telah diambil!":
            print("Username sudah digunakan. Coba username lain.")
            # Break out to prompt for new username
            username = input("Masukkan Username: ")
            break  # Exit the password loop to re-enter username
        elif decoded_message == "Berhasil bergabung ke chatroom!":
            print("Berhasil masuk ke chatroom.")
            logged_in = True
            break  # Exit the password loop to continue

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