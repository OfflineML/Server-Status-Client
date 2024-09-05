# Server Status Monitor Client

This is the client that sends status information to [Server Monitor](https://servermonitor.offlineml.com). It is used to integrate your servers with the [Server Monitor](https://servermonitor.offlineml.com) application.

## Prerequisites

- Python 3.8 or higher
- pip

## Installation

```bash
pip3 install -r requirements.txt
``` 

## Usage
Clone the repository using git:
```bash
git clone https://github.com/Tetraa-Group/Server-Status-Client.git
```

**Before running the client**, you need to download the config file which is named as `<your server name>_api_configs.json` from the [Server Monitor => Servers](https://servermonitor.offlineml.com) and copy it to the application directory (`Server-Status-Client`).

## Installation on Linux

You can use `systemd` service to install and run the client as a service.

```bash
sudo nano /etc/systemd/system/status_client.service
```

```bash
[Unit]
Description=Server Status Client
After=network.target

[Service]   
ExecStart=/usr/bin/python3 /path/to/client.py
WorkingDirectory=/path/to/
Restart=always
User=your_username
Group=your_groupname
Environment="PATH=/usr/bin:/usr/local/bin"

[Install]
WantedBy=multi-user.target  
```
### Usage
```bash
sudo systemctl daemon-reload
sudo systemctl enable status_client.service
sudo systemctl start status_client.service
```
