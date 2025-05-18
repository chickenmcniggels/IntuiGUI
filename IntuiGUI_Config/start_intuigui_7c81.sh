#!/bin/bash
# Script to launch LinuxCNC with the Mesa 7c81 configuration for IntuiGUI

# Change to the config directory
cd "$(dirname "$0")"

echo "========== IntuiGUI 7c81 Startup =========="
echo "Starting IntuiGUI with Mesa 7c81 configuration..."

# Check for LinuxCNC installation
if ! command -v linuxcnc &> /dev/null; then
    echo "Error: LinuxCNC is not installed or not in PATH!"
    echo "Please install LinuxCNC with: sudo apt-get install linuxcnc"
    exit 1
fi

# Check if the 7c81.ini file exists
if [ ! -f 7c81.ini ]; then
    echo "Error: 7c81.ini configuration file not found!"
    echo "Make sure you are running this script from the correct directory."
    echo "Current directory: $(pwd)"
    echo "Files in current directory: $(ls -la)"
    exit 1
fi

# Check if the 7c81.hal file exists
if [ ! -f 7c81.hal ]; then
    echo "Error: 7c81.hal configuration file not found!"
    echo "Make sure you are running this script from the correct directory."
    echo "Current directory: $(pwd)"
    echo "Files in current directory: $(ls -la)"
    exit 1
fi

# Check for mesaflash installation
if ! command -v mesaflash &> /dev/null; then
    echo "Error: mesaflash is not installed!"
    echo "Please install mesaflash with: sudo apt-get install mesaflash"
    echo "Then run setup_mesa_7c81.sh to configure the Mesa card."
    exit 1
fi

# Check for SPI interface enabled
if ! grep -q "dtparam=spi=on" /boot/config.txt 2>/dev/null; then
    echo "Warning: SPI may not be enabled in /boot/config.txt"
    echo "Run setup_mesa_7c81.sh as root to enable SPI and reboot."
fi

# Check for SPI device
if [ ! -e /dev/spidev0.0 ]; then
    echo "Warning: SPI device /dev/spidev0.0 not found!"
    echo "Please run 'sudo ./setup_mesa_7c81.sh' and reboot if necessary."
    echo "Continuing anyway, but LinuxCNC may not work properly without SPI."
fi

# Check if Mesa 7c81 is accessible - redirect stderr to avoid mesaflash errors in output
if ! mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --readhmid > /dev/null 2>&1; then
    echo "Warning: Unable to communicate with Mesa 7c81 card."
    echo "Please check connections and ensure the card is powered and properly connected."
    echo "Try running 'sudo ./setup_mesa_7c81.sh' to configure the system."
    echo "Continuing anyway, but LinuxCNC may not work properly."
else
    echo "Mesa 7c81 card detected successfully!"
fi

# Check user permissions for SPI device
if [ ! -w /dev/spidev0.0 ]; then
    echo "Warning: Current user ($(whoami)) does not have write permissions for /dev/spidev0.0"
    echo "This will cause communication problems with the Mesa card."
    echo "Fix with: sudo chmod a+rw /dev/spidev0.0"
    echo "Or run: sudo ./setup_mesa_7c81.sh"
    echo "Attempting to fix permissions automatically..."
    sudo chmod a+rw /dev/spidev0.0 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to set permissions automatically. Manual intervention required."
    else
        echo "Permissions updated successfully."
    fi
fi

# Launch LinuxCNC
echo "Starting LinuxCNC with 7c81 configuration..."
linuxcnc 7c81.ini

# Check if LinuxCNC exited with an error
if [ $? -ne 0 ]; then
    echo "LinuxCNC exited with an error. Check the log files for more information:"
    echo "- $HOME/linuxcnc_debug.txt"
    echo "- $HOME/linuxcnc_print.txt" 
    echo "- Run 'dmesg | tail' to see kernel messages"
    echo "If issues persist, run 'sudo ./setup_mesa_7c81.sh' to reconfigure the system."
fi

exit 0 