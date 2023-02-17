#!/usr/bin/bash
 
set -e

home="$(dirname "$0")/.."
source $home/.env
python=python$PYTHON_VERSION

mkdir $home/.venv
$python -m venv $home/.venv

source $home/.venv/bin/activate
pip install -r $home/requirements.txt

sudo apt install ffmpeg -y

# Install Systemd Service
sudo cat > /etc/systemd/system/ttsushi.service << EOF
[Unit]
Description=Talk-To-Sushi discord bot
After=network.target

[Service]
ExecStart=/usr/bin/bash $home/scripts/run.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload 
sudo systemctl enable ttsushi.service # remove the extension
sudo systemctl start ttsushi.service