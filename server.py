import socket
import threading

PASSWORD = "MasihPemula"
broadcast_port = 8888  # Listening port for client's desired server port

# Create a UDP socket for receiving the desired port
port_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port_listener.bind(('', broadcast_port))

# Wait for a client to broadcast the port
print("Waiting for client to broadcast desired port...")
message, addr = port_listener.recvfrom(1024)
server_port = int(message.decode())
print(f"Setting server port to {server_port} based on client input.")
port_listener.close()

server_ip = socket.gethostbyname(socket.gethostname())
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((server_ip, server_port))

clients = {}
username_set = set()

def broadcast_message(message, sender_addr=None):
    for client_addr in clients.keys():
        if client_addr != sender_addr:
            try:
                server.sendto(message.encode(), client_addr)
            except Exception as e:
                print(f"Error sending message to {client_addr}: {e}")

def perform_handshake(addr):
    print(f"Received SYN from {addr}. Sending SYN-ACK...")
    server.settimeout(3)  # Timeout for ACK response

    try:
        server.sendto("SYN-ACK".encode(), addr)
        ack, _ = server.recvfrom(1024)
        if ack.decode() == "ACK":
            print(f"Handshake completed successfully with {addr}.")
            return True
    except socket.timeout:
        print(f"Handshake failed with {addr}: No ACK received.")
        print("Possible reasons:")
        print("- Client may have disconnected before completing handshake.")
        print("- Network issues causing packet loss or delay.")
    finally:
        server.settimeout(None)  # Remove timeout after handshake attempt

    return False

def receive_message():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            decoded = message.decode()
            
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
                else:
                    server.sendto("Password salah!".encode(), addr)
                    print(f"Client {addr} attempted with wrong password")

            elif addr in clients:
                uname = clients.get(addr, "Unknown")
                if decoded == "Aku nak keluar":
                    broadcast_message(f"{uname} telah meninggalkan chatroom.")
                    print(f"{uname} ({addr}) left the chatroom.")
                    if addr in clients:
                        del clients[addr]
                        username_set.remove(uname)
                else:
                    broadcast_message(f"{uname}: {decoded}", sender_addr=addr)
                    print(f"Message from {uname}: {decoded}")
                    server.sendto("ACK".encode(), addr)
                    
        except ConnectionResetError:
            # Handle abrupt client disconnection
            if addr in clients:
                uname = clients.pop(addr)
                username_set.remove(uname)
                print(f"Client {addr} ({uname}) disconnected unexpectedly.")
                broadcast_message(f"{uname} has disconnected from the chat.")
        except KeyboardInterrupt:
            print("Server interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"Error receiving message: {e}")

t1 = threading.Thread(target=receive_message)
t1.daemon = True
t1.start()

try:
    t1.join()
except KeyboardInterrupt:
    print("Server shutting down.")
finally:
    server.close()
