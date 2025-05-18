#!/bin/bash
# Script to launch LinuxCNC with the Mesa 7c81 configuration for IntuiGUI

# Change to the config directory
cd "$(dirname "$0")"

# Check if the 7c81.ini file exists
if [ ! -f 7c81.ini ]; then
    echo "Error: 7c81.ini configuration file not found!"
    echo "Make sure you are running this script from the correct directory."
    exit 1
fi

# Check if the 7c81.hal file exists
if [ ! -f 7c81.hal ]; then
    echo "Error: 7c81.hal configuration file not found!"
    echo "Make sure you are running this script from the correct directory."
    exit 1
fi

# Check for SPI device
if [ ! -e /dev/spidev0.0 ]; then
    echo "Warning: SPI device /dev/spidev0.0 not found!"
    echo "Please run setup_mesa_7c81.sh as root and reboot if necessary."
    echo "Continuing anyway, but LinuxCNC may not work properly without SPI."
fi

# Check if Mesa 7c81 is accessible
if ! mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --readhmid &> /dev/null; then
    echo "Warning: Unable to communicate with Mesa 7c81 card."
    echo "Please check connections and run setup_mesa_7c81.sh if needed."
    echo "Continuing anyway, but LinuxCNC may not work properly."
fi

# Launch LinuxCNC
echo "Starting LinuxCNC with 7c81 configuration..."
linuxcnc 7c81.ini

exit 0 