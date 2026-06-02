#############################################################################################################


WAVE Protocol Overview

1. The client establishes a TCP connection with the WAVE server.

2. The client starts the handshake process by sending an NCS_key packet.

3. The server validates the handshake request.

4. If the device is already registered, the server accepts the connection.

5. If the device is not registered, the server starts the registration process.

6. The client sends an NCS_def_num packet containing the number of definition parts.

7. The server requests the device definition.

8. The client sends the device definition using one or more Partdef packets.

9. The server collects all definition parts and rebuilds the complete definition.

10. The server creates and loads a dedicated device handler dynamically.

11. The registration process is completed and the device becomes active.

12. The client periodically sends operational data using DCS_data packets.

13. The server validates and processes the received data.

14. The device-specific logic converts raw data into dashboard-ready values.

15. The processed data is displayed in the web dashboard.

16. Device activity and connection information are logged by the server.

17. Multiple devices can communicate with the server simultaneously.

18. New device types can be added without modifying the server source code.

Main Packet Types

- NCS_key      : Handshake and connection validation.
- NCS_def_num  : Number of definition packets.
- Partdef      : Device definition transfer.
- DCS_data     : Operational data transfer.

Main Features

- Dynamic device registration.
- Dynamic code deployment.
- Real-time data processing.
- Multi-device support.
- Web dashboard integration.
- Telegram notifications.
- Cloudflare tunnel support.
- Runtime module loading.
- Lightweight TCP-based communication.




also there is error code can device deal with it 

oxfferrorcode(number)

10011 - Invalid message length.
10022 - Invalid data length.
10033 - Invalid device status.
10044 - Packet processing failure.
10055 - Device definition collection failed.
10066 - Invalid definition information.
10077 - Unexpected registration packet.
10088 - Registration failed.
10099 - Handshake failed.
100910 - Invalid data packet.
100911 - Unauthorized packet type.
100912 - Internal server error.


# NOTE:
# This is only an example client implementation.
# You are free to build your own client based on your project requirements.
# However, make sure that your implementation follows the WAVE protocol specification.
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
