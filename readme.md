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
Before running the client, you need to download the config file which is named as `<your server name>_api_configs.json` from the [Server Monitor => Servers](https://servermonitor.offlineml.com) and copy it to the application directory which is the same directory as `client.py` is located.

```bash
python3 client.py
``` 
To run the client in the background, you can use `nohup` or `screen` or `tmux` or `systemd` service.

### Using nohup
```bash
nohup python3 client.py > client.log 2>&1 &
```

### Using systemd service

```bash
sudo nano /etc/systemd/system/client.service
```

```bash
[Unit]
Description=Client Service
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

```bash
sudo systemctl daemon-reload
sudo systemctl enable client.service
sudo systemctl start client.service
```