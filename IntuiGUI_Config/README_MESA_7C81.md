# IntuiGUI Mesa 7c81 Configuration

## Overview

This document provides instructions for setting up IntuiGUI with a Mesa 7c81 card, which is a Raspberry Pi-compatible FPGA card designed for LinuxCNC motion control.

## Hardware Requirements

- Raspberry Pi 4 (recommended) or Raspberry Pi 3B+
- Mesa 7c81 FPGA card
- Stepper motor drivers or servo drivers compatible with step/direction inputs
- Appropriate power supply for the Mesa card (5V)
- Appropriate power supply for motor drivers
- Limit switches (optional but recommended)
- Breakout board or appropriate wiring to connect the Mesa card to your motor drivers

## Software Setup

### 1. Install LinuxCNC

If you haven't already, install LinuxCNC 2.9 or later on your Raspberry Pi. Follow the installation instructions from the LinuxCNC website or use a pre-built image specifically for Raspberry Pi.

### 2. Set Up SPI Interface

The Mesa 7c81 card communicates with the Raspberry Pi via SPI. Run the setup script provided to configure the SPI interface:

```bash
sudo bash setup_mesa_7c81.sh
```

If prompted, reboot your system after running the script.

### 3. Flash Firmware to the Mesa Card

The Mesa 7c81 card requires appropriate firmware. You can use mesaflash to program the firmware:

```bash
sudo mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --write /path/to/firmware.bit
```

Replace `/path/to/firmware.bit` with the actual path to the firmware file. The typical firmware for a stepper-based system would be the `7c81_g540.bit` or similar.

### 4. Configure LinuxCNC

The following files in this directory are provided for configuring LinuxCNC with the Mesa 7c81 card:

- `7c81.ini` - Main configuration file
- `7c81.hal` - Hardware Abstraction Layer configuration
- `qtvcp_postgui.hal` - HAL commands to execute after the GUI has loaded

To use these configurations:

1. Make sure the files are in your LinuxCNC config directory (typically `/home/username/linuxcnc/configs/your-config-name/`)
2. Make the setup script executable: `chmod +x setup_mesa_7c81.sh`
3. Launch LinuxCNC from the terminal: `linuxcnc 7c81.ini`

## Pin Assignments

The Mesa 7c81 card provides numerous I/O pins. The default configuration in `7c81.hal` assigns pins as follows:

### Stepper Outputs

- X Axis Step: Pin 2 (hm2_7c81.0.stepgen.00.step)
- X Axis Direction: Pin 3 (hm2_7c81.0.stepgen.00.direction)
- Z Axis Step: Pin 4 (hm2_7c81.0.stepgen.01.step)
- Z Axis Direction: Pin 5 (hm2_7c81.0.stepgen.01.direction)
- Joint 2 Step: Pin 6 (hm2_7c81.0.stepgen.02.step) - Not used in basic lathe setup
- Joint 2 Direction: Pin 7 (hm2_7c81.0.stepgen.02.direction) - Not used in basic lathe setup

### Input Pins

- X Home/Limit: Pin 10 (hm2_7c81.0.gpio.001.in)
- Z Home/Limit: Pin 11 (hm2_7c81.0.gpio.004.in)
- E-Stop Input: Pin 12 (hm2_7c81.0.gpio.007.in)

### Output Pins

- Spindle Enable: Pin 14 (hm2_7c81.0.pwmgen.00.enable)
- Spindle PWM: Pin 16 (hm2_7c81.0.pwmgen.00.value)
- Spindle Direction: Pin 17 (hm2_7c81.0.gpio.010.out)

## Customization

You may need to customize the configuration files to match your specific hardware setup:

### Adjusting Stepper Parameters

Edit the `7c81.hal` file to adjust stepper parameters:

```
setp hm2_7c81.0.stepgen.00.dirsetup    200  # Adjust as needed
setp hm2_7c81.0.stepgen.00.dirhold     200  # Adjust as needed
setp hm2_7c81.0.stepgen.00.steplen     40   # Adjust as needed
setp hm2_7c81.0.stepgen.00.stepspace   40   # Adjust as needed
```

### Adjusting Input/Output Pin Assignments

Edit the `7c81.hal` file to change which pins connect to which functions. For example, to change which pin is connected to the X limit switch:

```
# Change this line
net x-home-sw <= hm2_7c81.0.gpio.001.in
# To use a different pin
net x-home-sw <= hm2_7c81.0.gpio.003.in
```

### Adjusting Machine Parameters

Edit the `7c81.ini` file to adjust machine parameters such as axis travel limits, homing speeds, etc.

## Troubleshooting

### SPI Communication Issues

If you encounter issues with SPI communication:

1. Verify that SPI is enabled: `ls -l /dev/spidev*`
2. Check SPI permissions: `ls -la /dev/spidev*`
3. Test communication with the card: `sudo mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --readhmid`

### Motor Issues

If motors do not move or behave erratically:

1. Check connections between the Mesa card and motor drivers
2. Verify step/direction signals with an oscilloscope if available
3. Adjust stepper timing parameters in the HAL file
4. Check that motor drivers are properly configured and powered

### Limit Switch Issues

If limit switches do not trigger or trigger incorrectly:

1. Check connections between switches and the Mesa card
2. Verify the configuration in the HAL file
3. Check if switches are normally open or normally closed and adjust the configuration accordingly

## Resources

- [LinuxCNC Documentation](http://linuxcnc.org/docs/)
- [Mesa Electronics Documentation](http://www.mesanet.com/documentation.html)
- [LinuxCNC Forum](https://forum.linuxcnc.org/)

## Support

For issues specific to this configuration, please refer to the LinuxCNC forum or the project's issue tracker.

---

Last Updated: 2023-10-15 