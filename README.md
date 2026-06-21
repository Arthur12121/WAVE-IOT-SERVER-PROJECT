# WAVE IoT Server v2.9

An IoT Device Management Server written in Python that provides:

* Secure device registration and authentication
* Dynamic device logic loading
* Real-time device communication
* Web dashboard monitoring
* Telegram notifications
* Cloudflare Tunnel integration
* Interactive device visualization

---

## Features

### Device Authentication

* Custom communication protocol
* Handshake verification
* Device ID registration
* Duplicate device detection

### Real-Time Communication

* TCP Socket Server
* Multiple client handling
* Event-driven architecture using selectors
* Dynamic packet processing

### Dynamic Device Logic

Each device can upload its own processing logic.

The server automatically:

* Receives device definitions
* Stores them as Python modules
* Loads them dynamically
* Executes device-specific handlers

### Web Dashboard

Monitor:

* Connected devices
* Device status
* Last seen timestamps
* Device IP addresses

### Telegram Integration

Receive notifications when:

* Server starts
* Cloudflare tunnel is created
* New devices connect
* Important events occur

### Cloudflare Tunnel

Automatically exposes the dashboard to the internet using:

* Cloudflare Tunnel
* Temporary public URL generation

### Interactive Visualization

Incoming device data can be displayed through interactive web pages.

---

# Project Structure

```text
WAVE/
│
├── main.py
├── token_id.txt
├── logid.txt
├── list of login.txt
│
├── locations/
│   ├── __init__.py
│   └── dynamic device modules
│
├── web/
│   ├── website.py
│   └── websitecontrol.py
│
└── cloudflared.exe
```

---

# Communication Protocol

Every packet starts with:

```text
0xAA
```

Packet format:

```text
IP-ID-PACKET_TYPE-STATUS-MSG_LENGTH-DATA_LENGTH-DATA
```

Example:

```text
192.168.1.10-device01-DCS_data-Active-50-12-temperature=25
```

---

# Packet Types

## NCS_key

Initial handshake packet.

Example:

```text
NCS_key
```

---

## NCS_def_num

Sends number of definition packets.

Example:

```text
num:5
```

---

## Partdef

Contains pieces of device definition data.

Used to upload:

* Device ID
* UI ID
* Python processing logic

---

## DCS_data

Normal operational data packet.

Used after successful registration.

---

# Device Registration Flow

```text
Device
   │
   ▼
Send NCS_key
   │
   ▼
Server Validation
   │
   ▼
New Device?
 ┌───────┴───────┐
 │               │
Yes             No
 │               │
 ▼               ▼
Upload       Direct Login
Definition
 │
 ▼
Store Module
 │
 ▼
Activate Device
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/WAVE.git
cd WAVE
```

## Install Requirements

```bash
pip install psutil requests
```

---

# Telegram Configuration

Create:

```text
token_id.txt
```

Example:

```text
BOT_TOKEN
CHAT_ID
```

Example:

```text
123456789:ABCDEFxxxxxxxxxxxxxxxx
987654321
```

---

# Running

```bash
python main.py
```

Startup menu:

```text
Do you want to change telegram token?
(Y/N)

Set Port:

Set IP:
1 - Device IP
2 - Localhost
```

---

# Dynamic Device Logic Example

Example uploaded by a device:

```python
temp = float(data[0])

if temp > 40:
    status = "HOT"
else:
    status = "NORMAL"
```

The server automatically converts it into:

```python
def device01(data):
    ...
```

and loads it dynamically.

---

# Logging

## Device IDs

```text
logid.txt
```

Stores registered device IDs.

## Connection Logs

```text
list of login.txt
```

Stores:

* Timestamp
* Device IP
* Device ID
* Packet Type

---

# Technologies Used

* Python
* Socket Programming
* Selectors
* Dynamic Imports
* Cloudflare Tunnel
* Telegram Bot API
* Requests
* Psutil
* Multithreading

---

# Security Notes

Current version includes:

* Handshake validation
* Device ID checking
* Packet length verification
* Status verification

Future improvements:

* AES Encryption
* TLS Communication
* JWT Authentication
* Device Certificates
* Rate Limiting

---

# Version

```text
WAVE v2.9
```

Created by:

```text
arthur12121
```

First custom IoT server project focused on dynamic device registration, monitoring, and visualization.
