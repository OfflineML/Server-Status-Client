#!/bin/bash

# Check if required argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <app_version>"
    exit 1
fi

# Define variables
APP_VERSION=$1
DOWNLOAD_URL="https://github.com/Tetraa-Group/Server-Status-Client/releases/download/${APP_VERSION}/client"
ENDPOINT="https://api.statusrecorder.ziphio.com/server_data"  # Replace with actual config API URL
INSTALL_DIR="/opt/server-status-client"
SERVICE_NAME="server-status-client"

# Prompt user for API key
read -p "Enter your API key: " API_KEY

# Remove existing installation directory if it exists
sudo rm -rf $INSTALL_DIR

# Create installation directory
sudo mkdir -p $INSTALL_DIR

# Download the client
sudo wget $DOWNLOAD_URL -O $INSTALL_DIR/client

# Make the client executable
sudo chmod +x $INSTALL_DIR/client

# Create api_configs.json file
cat << EOF | sudo tee $INSTALL_DIR/api_configs.json
{
  "api_key": "$API_KEY",
  "endpoint": "$ENDPOINT"
}
EOF

# Create systemd service file
cat << EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=Server Status Client
After=network.target

[Service]
ExecStart=$INSTALL_DIR/client
WorkingDirectory=$INSTALL_DIR
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Server Status Client has been installed and started as a service."
echo
echo "To manage the Server Status Client service:"
echo "  Start the service:   sudo systemctl start $SERVICE_NAME"
echo "  Stop the service:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart the service: sudo systemctl restart $SERVICE_NAME"
echo "  Check status:        sudo systemctl status $SERVICE_NAME"
echo
echo "The service is configured to start automatically on system boot."
echo "You can view the logs using: sudo journalctl -u $SERVICE_NAME"
