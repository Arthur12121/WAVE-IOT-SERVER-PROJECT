#############################################################################################################

# NOTE:
# This is only an example client implementation.
# You are free to build your own client based on your project requirements.
# However, make sure that your implementation follows the WAVE protocol specification.
#
# This example demonstrates how a client communicates with the server,
# registers itself, uploads its logic, and sends data.


import socket
import time
import json

def build_packet(ip, device_id, packet_type, status, data):
    magic = "0xAA"
    data_str = str(data)
    data_len = str(len(data_str))
    msg_len = "1038"

    header = f"{ip}-{device_id}-{packet_type}-{status}-{msg_len}-{data_len}-{data_str}"
    header = header.ljust(1038, " ")

    return magic.encode(), header.encode()

def run_client():
    server_ip = ""             #SERVER IP
    server_port = 7070         #SERVER PORT

    device_id = ""             # YOU CAN CREATE ID BY YOURSELF MAKE SURE DONT MAKE TWO CONTROLLER WITH SAME ID
    device_ip = ""             # HERE THE IP OF DEVICE

    sock = socket.socket()
    sock.connect((server_ip, server_port))

    print("[+] Connected to server")

    
    magic, header = build_packet(device_ip, device_id, "NCS_key", "Active", "4343")
    sock.sendall(magic)
    sock.sendall(header)

    resp = sock.recv(1024).decode(errors="ignore")
    print("[SERVER]", resp)

    
    if "serverwelcomeyou" in resp:

        logic_payload = {
            "id": device_id,
            "ui_id": "degree",

            "code": (
                "parts = data.split(',')\n"
                "result = [\n"
                "     int(parts[0]),\n"
                "     int(parts[1]),\n"
                "     int(parts[2])\n"
                "]\n"
                'namelist = ["name1", "name2" , "name3"]\n'
                "data = [namelist , result]"         
            )
        }

        json_string = json.dumps(logic_payload)

        chunk_size = 500
        chunks = [json_string[i:i+chunk_size] for i in range(0, len(json_string), chunk_size)]
        num = len(chunks)

      
        magic, header = build_packet(device_ip, device_id, "NCS_def_num", "Active", f"num:{num}")
        sock.sendall(magic)
        sock.sendall(header)

       
        for i, chunk in enumerate(chunks):
            server_signal = sock.recv(1024).decode(errors="ignore")

            if "serverneeddef" in server_signal or "serversaynext" in server_signal:
                magic, header = build_packet(device_ip, device_id, "Partdef", "Active", chunk)
                sock.sendall(magic)
                sock.sendall(header)
                print(f"[>] sent part {i+1}/{num}")

        print("[+] Code configuration sent successfully")

    
    print("[+] sending sensor data...")
    while True:

        payload = "80,32,1332" #example

        magic, header = build_packet(device_ip, device_id, "DCS_data", "Active", payload)
        sock.sendall(magic)
        sock.sendall(header)

        print("[>] sent:", payload)
        time.sleep(3)

if __name__ == "__main__":
    run_client()
###############################################################################################################