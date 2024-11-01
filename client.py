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
            decoded_message = message.decode()
            if decoded_message == "ACK":
                print("Server acknowledged message.")
            else:
                print(decoded_message)
        except socket.error as e:
            if not stop_receive:
                print(f"Error receiving from server: {e}")
                break

def initiate_handshake():
    print("Initiating handshake...")
    attempts = 3  # Number of handshake attempts
    client.settimeout(3)  # Timeout for each attempt

    for attempt in range(1, attempts + 1):
        try:
            print(f"Handshake attempt {attempt} of {attempts}")
            client.sendto("SYN".encode(), address)
            response, _ = client.recvfrom(1024)
            
            if response.decode() == "SYN-ACK":
                print("Received SYN-ACK, sending ACK to complete handshake.")
                client.sendto("ACK".encode(), address)
                client.settimeout(None)  # Disable timeout after handshake
                print("Handshake completed successfully.")
                return True
        except socket.timeout:
            print(f"Attempt {attempt} failed: No response from server. Retrying...")
        except ConnectionResetError:
            print("Connection was forcibly closed by the remote host. Possible reasons:")
            print("- The server port may be incorrect or unreachable.")
            print("- The server may be offline or not listening on the specified port.")
            return False
        except socket.error as e:
            print(f"An unexpected socket error occurred: {e}")
            return False
    
    # Handshake failed after maximum attempts
    print("Handshake failed after maximum attempts. Possible issues could be:")
    print("- Server is offline or unreachable.")
    print("- Incorrect server IP or port.")
    print("- Network issues causing packet loss.")
    return False

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('', random.randint(8000, 9000)))

# Perform handshake and exit if handshake fails
if not initiate_handshake():
    client.close()
    exit()

logged_in = False
while not logged_in:
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

# Start receiving messages in a separate thread
t = threading.Thread(target=receive_message)
t.daemon = True
t.start()

try:
    while not stop_receive:
        message = input()
        if message == "Aku nak keluar":
            print("Leaving chat room...")
            client.sendto(message.encode(), address)
            stop_receive = True
        else:
            client.sendto(message.encode(), address)
except KeyboardInterrupt:
    print("Client interrupted. Exiting...")
finally:
    stop_receive = True
    client.close()
    t.join()
