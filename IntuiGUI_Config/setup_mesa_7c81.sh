#!/bin/bash
# Setup script for Mesa 7c81 SPI interface
# This script prepares the SPI interface for the Mesa 7c81 card on Raspberry Pi

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

echo "Setting up SPI interface for Mesa 7c81 card..."

# Enable SPI interface if not already enabled
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "Enabling SPI interface in /boot/config.txt"
    echo "dtparam=spi=on" >> /boot/config.txt
    echo "SPI interface enabled. A reboot will be required after this script completes."
    REBOOT_REQUIRED=true
else
    echo "SPI interface already enabled in /boot/config.txt"
fi

# Check if SPI kernel module is loaded
if ! lsmod | grep -q "spi_"; then
    echo "Loading SPI kernel module"
    modprobe spi-bcm2835
    modprobe spidev
fi

# Check if SPI device exists
if [ ! -e /dev/spidev0.0 ]; then
    echo "Error: SPI device /dev/spidev0.0 not found!"
    echo "Please reboot your system to activate the SPI interface."
    exit 1
fi

# Set permissions for the SPI device
echo "Setting permissions for SPI device"
chmod 666 /dev/spidev0.0

# Install mesaflash if not already installed
if ! command -v mesaflash &> /dev/null; then
    echo "Installing mesaflash..."
    apt-get update
    apt-get install -y mesaflash
else
    echo "mesaflash already installed"
fi

# Check if Mesa 7c81 card is detected
echo "Testing communication with Mesa 7c81 card..."
if mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --readhmid &> /dev/null; then
    echo "Mesa 7c81 card detected successfully!"
else
    echo "Error: Unable to communicate with Mesa 7c81 card."
    echo "Please check your connections and ensure the card is properly connected."
    exit 1
fi

# Create udev rule for persistent permissions
echo "Creating udev rule for persistent permissions..."
cat > /etc/udev/rules.d/99-mesa-7c81.rules << EOF
KERNEL=="spidev0.0", MODE="0666"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

echo "Setup complete!"
if [ "$REBOOT_REQUIRED" = true ]; then
    echo "Please reboot your system now to complete the setup."
fi

exit 0 