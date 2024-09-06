#!/bin/bash
# Check if required argument is provided
# Prompt user for API Key
read -p "Please enter your Server's API Key: " API_KEY

# Validate API Key input
if [ -z "$API_KEY" ]; then
    echo -e "\e[31mAPI Key is required.\e[0m"
    exit 1
fi


if [ $# -ne 1 ]; then
    echo -e "\e[31mUsage: $0 APP_VERSION\e[0m"
    exit 1
fi

# Define variables
APP_VERSION=$1

DOWNLOAD_URL="https://github.com/Tetraa-Group/Server-Status-Client/releases/download/${APP_VERSION}/linux_client"
ENDPOINT="https://api.statusrecorder.ziphio.com/server_data"  # Replace with actual config API URL
INSTALL_DIR="/opt/server-status-client"
SERVICE_NAME="server-status-client"

# Remove existing installation directory if it exists
sudo rm -rf $INSTALL_DIR

# Create installation directory
sudo mkdir -p $INSTALL_DIR

# Download the client
sudo wget $DOWNLOAD_URL -O $INSTALL_DIR/linux_client

# Make the client executable
sudo chmod +x $INSTALL_DIR/linux_client

# Create api_configs.json file
cat << EOF | sudo tee $INSTALL_DIR/api_configs.json
{  
    "version": "$APP_VERSION",
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
ExecStart=$INSTALL_DIR/linux_client
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
sudo systemctl restart $SERVICE_NAME

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
