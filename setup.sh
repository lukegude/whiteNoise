#!/bin/bash

# Exit on error
set -e

echo "Setting up WhiteNoise application..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user is in a group
user_in_group() {
    groups $USER | grep -q "\b$1\b"
}

# Install Python if not present
if ! command_exists python3.10; then
    echo "Installing Python 3.10..."
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3-pip
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.10 -m venv venv
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    libasound2-dev \
    pulseaudio \
    sox \
    libsox-fmt-all \
    bluez \
    bluez-tools \
    pulseaudio-module-bluetooth \
    expect \
    libbluetooth-dev \
    build-essential \
    dbus-x11 \
    dbus \
    alsa-utils \
    libasound2-plugins \
    pulseaudio-utils

# Add user to necessary groups
echo "Adding user to audio groups..."
for group in audio pulse pulse-access bluetooth lp; do
    if ! user_in_group $group; then
        sudo usermod -aG $group $USER
    fi
done

# Configure PulseAudio
echo "Configuring PulseAudio..."
sudo mkdir -p /etc/pulse
sudo tee /etc/pulse/system.pa > /dev/null << EOL
load-module module-native-protocol-unix auth-anonymous=1
load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;192.168.0.0/16
load-module module-alsa-sink device=hw:0,0
load-module module-alsa-source device=hw:0,0
EOL

# Compile the C program
echo "Compiling whitenoise.c..."
gcc whitenoise.c -o out

# Install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
echo 'export FLASK_APP=app.py' >> ~/.bashrc
echo 'export FLASK_RUN_HOST=0.0.0.0' >> ~/.bashrc
echo 'export FLASK_ENV=production' >> ~/.bashrc

echo "Setup complete! Please log out and log back in for group changes to take effect."
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the application: flask run"
