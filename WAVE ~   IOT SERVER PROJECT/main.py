import subprocess
import socket
import selectors
import types
import psutil
from web.websitecontrol import start_dashboard 
import datetime
import os
import importlib
import sys
import textwrap
import datetime
from web.website import start_interactive_site
import json
import threading
import subprocess
import requests
import re

def tocken_from_file():
   with open("token_id.txt" , 'r') as f:
    result = f.read().splitlines()
    return result[0]
   
def chat_id_from_file():
   with open("token_id.txt" , 'r') as f:
    result = f.read().splitlines()
    return result[0]

TOKEN = str(tocken_from_file) 
CHAT_ID = str(chat_id_from_file()) 

web_hook = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
photo_hook = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
update_hook = f"https://api.telegram.org/bot{TOKEN}/getUpdates"


def start_cloudflare_tunnel(ip):
    ip = str(ip)
    port = int(port)
    global tunnel_proc
    proc = subprocess.Popen(
        ["cloudflared.exe", "tunnel", "--url", f"http://{ip}:5000"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
    )
    tunnel_proc = proc
    for line in proc.stdout:
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match: 
            text = f"WAVE _/ \n the system is ready \n you can enter the link \n {match.group()} "
            send_http(text)
    return None


active_dict = {}

def cpu_usage_percent():
    return int(psutil.cpu_percent(interval=1))

def log_conn(ip, id , typepacket):
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"Time: {now} | IP: {ip} | ID: {id} | packet type: {typepacket}\n"
        with open("list of login.txt", "a") as f:
            f.write(line)
    except:
        pass

def extract_protocol_fields(payload: str):
    try:
        parts = [p.strip() for p in payload.split("-", 6)]
        if len(parts) < 7:
            return None

        return parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
    except:
        return None

def ip_get():
    try:
        cmd_ip = subprocess.check_output("ipconfig", shell=True).decode()
        for line in cmd_ip.splitlines():
            line = line.strip()
            if line.startswith("IPv4 Address"):
                return line.split(":")[-1].strip()
    except:
        pass
    return "127.0.0.1"
    
def remove_id(user_id, filename="logid.txt"):
    if not os.path.exists(filename):
        return

    with open(filename, "r") as f:
        ids = f.read().splitlines()

    if user_id in ids:
        ids.remove(user_id)
        with open(filename, "w") as f:
            for i in ids:
                f.write(i + "\n")

def check_id(user_id, filename="logid.txt"):
    if not os.path.exists(filename):
        open(filename, "w").close()

    with open(filename, "r") as f:
        ids = f.read().splitlines()

    if user_id in ids:
        return True
    
    else:

        with open(filename, "a") as f:
            f.write(user_id + "\n")
        return False

def msgchecker(conn):
    try:
        magic_word = conn.recv(4).decode(errors="ignore")

        if magic_word != "0xAA":
            return None

        header = conn.recv(1038).decode(errors="ignore")

        fields = extract_protocol_fields(header)

        if fields is None:
            return None
        
        ip , id , packetype , status , msglanth , lenth , data = fields
        
        if str(msglanth) != str(len(header)):
            conn.sendall(b"0xFFerrorcode10011")
            return None

        if str(lenth) != str(len(data)):
            print(str(lenth) , str(len(data)+1))
            conn.sendall(b"0xFFerrorcode10022")
            return None

        if status != "Active":
            conn.sendall(b"0xFFerrorcode10033")
            return None

        resulte = check_id(str(id))

        return ip , packetype , resulte , data , id

    except Exception as e:
        try:
            conn.sendall(b"0xfferrorcode10044")
        except:
            pass
        return None


def save_device_location(device_id, ui_id, logic_code):
    try:
        if not os.path.exists("locations"):
            os.makedirs("locations")
            with open("locations/__init__.py", "w") as f: pass

        filename = f"locations/{device_id}.py"
        
        indented_logic = textwrap.indent(textwrap.dedent(logic_code).strip(), '    ')

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"def {device_id}(data):\n")
            f.write(f"{indented_logic}\n")
            f.write(f"    return '{device_id}', data[0] , data[1], '{ui_id}'\n")

        importlib.invalidate_caches()
    except:
        pass

def get_device_handler(device_id):
    try:
        module_name = f"locations.{device_id}"

        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)

        if hasattr(module, device_id):
            return getattr(module, device_id)

        return None

    except Exception as e:
        print("Handler load error:", e)
        return None
    
def run_id_logic(id, data):
    try:
        module_name = f"locations.{id}"
        
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)
        
        func = getattr(module, id)
        return func(data)
        
    except Exception as e:
        return f"Error: {e}"
    

def collection_part_def(conn, number):
    try:
        conn.sendall(b"0xffserverneeddef")
        pylod = ""
        i = 0

        while i < number:
            result = msgchecker(conn)
            if not result:
                break

            ip, packetype, resulteid, data, id_msg = result
            
            if packetype == "Partdef":
                pylod += data
                i += 1
                if i < number:
                    conn.sendall(b"0xFFserversaynext")
            else:
                continue

        full_data = json.loads(pylod)
        
        r_id = full_data.get("id")
        r_code = full_data.get("code")
        r_ui_id = full_data.get("ui_id")

        return r_id, r_code, r_ui_id

    except Exception:
        try:
            conn.sendall(b"0xfferrorcode10055")
            
            conn.close()
        except:
            pass
        return None, None, None

def new_connection(sock, selec): #0xAA - IP - ID - PACKET TYEP - STATUS - DATA TYPE - LENTH - DATA 
    try:
        conn, addr = sock.accept()

        if conn:
         print(f"[+] new connection from {addr}")

         ip , packetype , resulteid , data , id = msgchecker(conn)
         
         if packetype == "NCS_key":
              
            if str(data) == "4343":

                if resulteid == True:
                 data_new_sign = types.SimpleNamespace(
                 conn=conn,
                 addr=addr,
                 inb=b"",
                 outb=b""
                 )
               
                 selec.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data_new_sign)

                 log_conn(ip , id , packetype)
                 conn.sendall(b"0xFFserveracceptyou")
               
                 print(f"[+] new device: {id , ip} has complete handshak")
                 active_dict[id] = {"ip": ip, "status": "CONNECTED", "last_seen": datetime.datetime.now().strftime("%H:%M:%S")}

                elif resulteid == False:
                 try:
                  
                  conn.sendall(b"0xFFserverwelcomeyou")

                  ip , packetype , resulteid , data , id = msgchecker(conn)

                  if packetype == "NCS_def_num" and resulteid == True and data.startswith("num:"):
                     try:
                      
                      try:
                     
                       num_of_packet = int(data.split(":")[1])
                       print(num_of_packet)

                      except (ValueError , IndexError):
                          conn.sendall(b"0xfferrorcode10066")
                          try:
                           conn.close()

                          except:
                              pass
                          
                      Fulldef = collection_part_def(conn , num_of_packet)
                     
                      active_dict[id] = {
                      "ip": ip,
                      "status": "CONNECTED",
                      "last_seen": datetime.datetime.now().strftime("%H:%M:%S")
                      }
                    
                      ids , code , ui_id = Fulldef
                      print(ids , code , ui_id)

                      save_device_location(ids , ui_id , code)

                      data_new_sign = types.SimpleNamespace(
                      conn=conn,
                      addr=addr,
                      inb=b"",
                      outb=b""
                      )
               
                      selec.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data_new_sign)

                      log_conn(ip , id , packetype)
                      conn.sendall(b"0xFFserverwelcomeyoucomp")

                     except Exception:
                         conn.sendall(b"0xfferrorcode10066")
                         
                  else:
                      
                    conn.sendall(b"0xfferrorcode10077")
                    conn.close()
                 except:
                     conn.sendall(b"0xfferrorcode10088")
                     conn.close()
            else:
                remove_id(id)
                conn.sendall(b"0xFFerrorcode10099")
                conn.close()
                
         else:
             print("error in new_connection")
             conn.close()
        else: 
            print("[!] its not iot device didnt start with 0XAA")
            conn.close()
    except:
        try:
            conn.close()
        except:
            pass


def service_connection(conn, mask, selec):
    global active_dict

    try:
        if not (mask & selectors.EVENT_READ):
            return

        result = msgchecker(conn)
        
        if not result:
            conn.sendall(b"0xfferrorcode100910")
            conn.close()
            return

        ip, packetype, resulteid, data, id = result

        if packetype == "DCS_data" and resulteid == True:
            
         print(ip, packetype, resulteid, data, id)

         resultsss = run_id_logic(id , data)

         id , ui_id , namelist ,datalist = resultsss

         print( "yep i get this",resultsss)

         start_interactive_site(id , ui_id , namelist , datalist)

        else:
            conn.sendall(b"0xfferrorcode100911")
            try:
             selec.unregister(conn)
            except:
             pass
             conn.close()
            return

    except Exception as e:
        print("Service error:", e)
        try:
            selec.unregister(conn)
        except:
            pass
        if 'id' in locals():
         active_dict.pop(id, None)
         conn.close()


def send_http(text):
    try: requests.post(web_hook, data={"chat_id": CHAT_ID, "text": text})
    except: pass

def recv_http():
    global last_update_id
    try:
        res = requests.get(f"{update_hook}?offset={last_update_id + 1}", timeout=10)
        data = res.json()
        if data["result"]:
            last_update = data["result"][-1]
            last_update_id = last_update["update_id"]
            return last_update["message"]["text"]
    except: pass
    return None


def edit_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    token = lines[0] if len(lines) > 0 else ""
    chat_id = lines[1] if len(lines) > 1 else ""

    choice = input("1-token 2-chat_id 3-both: ")

    if choice == "1":
        token = input("new token: ")

    elif choice == "2":
        chat_id = input("new chat_id: ")

    elif choice == "3":
        token = input("new token: ")
        chat_id = input("new chat_id: ")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(token + "\n")
        f.write(chat_id + "\n")


def logo():

    logo = """
############################################################################################
############################################################################################
############################################################################################
############################################################################################
####################=      #################################################################
####################.  ..  *#############  -###  -##*  ###   *##  *###*  *      *###########
####################. :#+  *#############-  ##-   *#- .##:    ##:  ###  -#  *###############
################*     :#+  *#*     *######  -*  : :*  *##  #  -##  -#*  ##  *###############
#################=...-##+  *#-  ..-#######*  = :+  - :##  -#*  *#+  #  +##      ############
########################+  *#-  ###########    ##:   +#=       :##:   :###  *###############
########################+       ###########-  =###  .#*  +####  -##   *###      +###########
#########################=     *############################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

###############################     WAVE V2.9     ##########################################
              
                            its my first IOT SERVER PROJECT
                                   by arthur12121
                          
"""
    return logo

def start_system():

    print(logo())

    while True:
     try:
      tele = str(input("do you want to chenge the token telegram (Y/N)? \n"))
      if tele.lower() == "yes" or tele.lower() == "y":
          edit_config("token_id.txt")
      elif tele.lower() == "no" or tele.lower() == "n":
          pass
      else:
          print("error")

      port = int(input("set the port: "))
      ip = str(input("set the IP \n 1 - use defult ip (the device ip) \n 2 - localhost \n "))
      
      if ip == "1":
        return str(ip_get()) , port
      elif ip == "2":
        return "127.0.0.1" , port
      else:
          print("error")
     except ValueError as e:
         print(e)
     except Exception as s:
         print(s)


def main(ip , port):
    global active_dict
    
    try:
        start_dashboard(active_dict, ip_get()) 

        threading.Thread(
    target=start_cloudflare_tunnel,
    args=("127.0.0.1"),
    daemon=True
).start()
    
        selec = selectors.DefaultSelector()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        server.bind((ip , port))
        server.listen()
        selec.register(server, selectors.EVENT_READ, data=None)
        
        print(f"server start: {ip}:{port}")

        while True:
            events = selec.select()
            for key, mask in events:
                if key.data is None:
                    new_connection(key.fileobj, selec)
                else:
                    service_connection(key.fileobj, mask, selec)

    except Exception as e:
        try:
         print("server error: ",e)
         sock = key.fileobj
         sock.close()
         
        except Exception:
            sock.close()
            sock.sendall(b"0xfferrorcode100912")
            
if __name__ == "__main__":
    ip , port = start_system()
    main(ip , port)