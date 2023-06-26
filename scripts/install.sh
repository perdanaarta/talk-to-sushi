#!/bin/bash

home="$(dirname "$0")/.."

# Check if FFMpeg is installed
if ! command -v ffmpeg &>/dev/null; then
  echo "FFMpeg is not installed. Installing FFMpeg..."
  sudo apt-get update
  sudo apt-get install ffmpeg -y
fi

# Check if Python is installed
if ! command -v python3.10 &>/dev/null; then
  echo "Python is not installed. Installing Python..."
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt-get update
  sudo apt-get install python3.10 -y
fi

# Create virtual environment
echo "Creating virtual environment..."
python3.10 -m venv $home/.venv
source $home/.venv/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install --upgrade -r $home/requirements.txt

# Set log file
echo "Setting log file..."
touch $home/logs/latest.log

# Create systemd service file
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/sushiai.service <<EOF
[Unit]
Description=Sushi AI Text To Speech Bot
After=network.target

[Service]
ExecStart=$home/scripts/run.sh
WorkingDirectory=$home
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload 
sudo systemctl enable sushiai.service
sudo systemctl start sushiai.service