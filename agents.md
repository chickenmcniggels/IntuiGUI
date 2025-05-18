# IntuiGUI - Agent Instructions

## Project Overview
IntuiGUI is a custom touchscreen interface designed specifically for lathe machines, built using QtVCP (Qt Virtual Control Panel) for LinuxCNC. The interface is optimized for portrait mode displays and aims to provide seamless integration with LinuxCNC systems. It's designed to run on a Raspberry Pi 5 with a Waveshare 10.1-inch touchscreen connected through MIPI DSI.

## Repository Information
- **GitHub URL**: https://github.com/chickenmcniggels/IntuiGUI.git
- **License**: GPL-3.0
- **Workflow**: Use feature branches for development. Create a branch for each feature or bugfix, then submit a pull request to the main branch when complete.

## Development Environment
- **OS**: Debian 12 Bookworm with PREEMPT-RT kernel (LinuxCNC 2.9.4)
- **Python**: 3.11.2
- **GUI Framework**: PyQt5 with QtVCP
- **Development Platform**: Windows with Cursor IDE
- **Deployment Platform**: Raspberry Pi 5

## SSH Connection Details
- **Host**: raspberrypi
- **User**: cnc
- **Password**: cnc
- **Port**: 22 (default)
- **File Deployment Locations**:
  - IntuiGUI_Config: `/home/cnc/linuxcnc/configs/IntuiGUI_Config/`
  - IntuiGUI: `/usr/share/qtvcp/screens/IntuiGUI/`
  - Widgets: `/usr/lib/python3/dist-packages/qtvcp/widgets`

## Hardware Configuration
- **Processor**: Raspberry Pi 5
- **Display**: Waveshare 10.1-inch Capacitive Touch Display, 1280×800, IPS, DSI Interface (in portrait mode)
- **Machine Control**: Mesa 7c81 FPGA Card connected to a db25 breakout board (temporary)
- **Future Hardware**: Custom PCB centered around the Compute Module 5
- **Machine Input**: Hardware encoder (MPG) for manual jogging

## User Interface Specifications
- **Resolution**: 1280×800 (portrait orientation)
- **Design Inspiration**: Datron Next (modern, touch-optimized)
- **UI Structure**: App-like tabs accessible from a home screen

## Project Goals
### Short-term
- Implement minimal but complete functionality
- Enable complete workflow support
- Ensure stability and reliability

### Long-term
- Simplify lathe job setup process
- Eliminate sources of human error
- Create deterministic, real-time capable, stable, reliable software for production lathes
- Custom PCB will be designed around Compute Module 5 and the software

## Features and Functionality
The UI consists of several main sections:

1. **Home Screen**: Central navigation point with app-like tabs
2. **Machine Tab**: For manual machine control
   - Support for hardware MPG encoder for jogging
3. **CAM Wizard Tab**: 5-step guide through cam job setup
4. **Settings Tab**: For non-job-specific machine configurations
5. **Makros Tab**: Predefined lathe cycles for basic operations without CAM software
6. **Status Tab**: Job metrics and live camera feed

## Development Workflow
1. **Code Development**: Develop and test on Windows with Cursor IDE
2. **Version Control**: Use GitHub for version management
3. **Automatic Deployment**: 
   - Changes pushed to the main branch are automatically deployed to the Raspberry Pi via GitHub Actions
   - A self-hosted GitHub runner on your local network handles the deployment
   - The runner connects to the Pi via SSH using its local hostname (raspberrypi)
   - The deployment script automatically syncs files to their respective locations on the Pi
   - No manual deployment needed for development
4. **Testing**: Run the code on the Raspberry Pi to test functionality
5. **Documentation**: Update documentation with any changes

## Code Standards
1. **Style and Format**: Custom widgets should follow the coding style of existing widgets
2. **Documentation**: Always update documentation when changes are made
3. **Commit Messages**: Use descriptive commit messages
4. **Reference**: Always check official documentation before implementing new features

## LinuxCNC Configuration
- The HAL configuration is located in the IntuiGUI_Config folder
- Integration with Mesa 7c81 FPGA Card
- Real-time kernel usage

## Testing Guidance
- Deploy to Raspberry Pi for full system testing
- User verifies all touchscreen functionality works as expected
- Ensure performance is adequate on the Pi

## Documentation References
### QtVCP Documentation
- [QtVCP Overview](https://linuxcnc.org/docs/devel/html/gui/qtvcp.html)
- [QtVCP Widgets](https://linuxcnc.org/docs/devel/html/gui/qtvcp-widgets.html)
- [QtVCP Libraries](https://linuxcnc.org/docs/devel/html/gui/qtvcp-libraries.html)
- [Qt Vismach](https://linuxcnc.org/docs/devel/html/gui/qtvcp-vismach.html)
- [Handler File Code Snippets](https://linuxcnc.org/docs/devel/html/gui/qtvcp-code-snippets.html)
- [QtVCP Development](https://linuxcnc.org/docs/devel/html/gui/qtvcp-development.html)
- [QtVCP Custom Widgets](https://linuxcnc.org/docs/devel/html/gui/qtvcp-custom-widgets.html)

### LinuxCNC Documentation
- [LinuxCNC Documentation](https://linuxcnc.org/docs/stable/html/)

## Important Notes
1. **ALWAYS reference the official Qt, QtVCP, and LinuxCNC documentation** before implementing new features
2. The interface must be deterministic, real-time capable, stable and reliable as it's running on production lathes
3. The UI is specifically designed for the Waveshare 10.1-inch touchscreen in portrait orientation
4. The code will be running on Debian Linux with a real-time kernel 
5. Use the MCPs when appropriate.

# Agents

IntuiGUI is designed to be modular and extensible. This document outlines different solutions for working with IntuiGUI.

## Mesa 7c81 Minimal Configuration

This section describes a minimal working configuration for the Mesa 7c81 card based on atdragon's approach.

### Hardware Requirements

- Raspberry Pi 3B+/4B
- Mesa 7c81 FPGA card
- Stepper motors and drivers (or servo motors and drivers)
- 5V power supply for Mesa card
- Appropriate power supply for motors

### Software Configuration Files

The Mesa 7c81 configuration consists of three main files:

1. **7c81.ini** - The INI file that defines the machine parameters
2. **7c81.hal** - The HAL file that configures the hardware abstraction layer for the Mesa card
3. **setup_mesa_7c81.sh** - A script to set up the SPI interface

#### 7c81.ini (Key Sections)

```ini
[EMC]
VERSION = 1.1
MACHINE = IntuiGUI-Lathe-7c81
DEBUG = 0x00002000

[DISPLAY]
DISPLAY = qtvcp -d IntuiGUI
PREFERENCE_FILE_PATH = WORKINGFOLDER/IntuiGUI.pref
CYCLE_TIME = 0.100

[FILTER]
PROGRAM_EXTENSION = .ngc,.nc,.tap G-Code Files
PROGRAM_EXTENSION = .png,.gif,.jpg Greyscale Depth Image
png = image-to-gcode
gif = image-to-gcode
jpg = image-to-gcode

[RS274NGC]
PARAMETER_FILE = linuxcnc.var
SUBROUTINE_PATH = subroutines
USER_M_PATH = mcodes

[EMCMOT]
EMCMOT = motmod
COMM_TIMEOUT = 1.0
SERVO_PERIOD = 1000000

[TASK]
TASK = milltask
CYCLE_TIME = 0.010

[HAL]
HALFILE = 7c81.hal
HALFILE = qtvcp_postgui.hal

[TRAJ]
COORDINATES = X Z
LINEAR_UNITS = mm
ANGULAR_UNITS = degree
MAX_LINEAR_VELOCITY = 100.00
DEFAULT_LINEAR_VELOCITY = 50.00

[KINS]
KINEMATICS = trivkins coordinates=XZ
JOINTS = 2

# X Axis
[AXIS_X]
MIN_LIMIT = -200.0
MAX_LIMIT = 200.0
MAX_VELOCITY = 100.0
MAX_ACCELERATION = 500.0

[JOINT_0]
TYPE = LINEAR
HOME = 0.0
MAX_VELOCITY = 100.0
MAX_ACCELERATION = 500.0
STEPGEN_MAXACCEL = 750.0
SCALE = 1000.0
FERROR = 1.0
MIN_FERROR = 0.5
MIN_LIMIT = -200.0
MAX_LIMIT = 200.0
HOME_OFFSET = 0.0
HOME_SEARCH_VEL = 50.0
HOME_LATCH_VEL = -5.0
HOME_SEQUENCE = 1

# Z Axis
[AXIS_Z]
MIN_LIMIT = -400.0
MAX_LIMIT = 0.0
MAX_VELOCITY = 100.0
MAX_ACCELERATION = 500.0

[JOINT_1]
TYPE = LINEAR
HOME = 0.0
MAX_VELOCITY = 100.0
MAX_ACCELERATION = 500.0
STEPGEN_MAXACCEL = 750.0
SCALE = 1000.0
FERROR = 1.0
MIN_FERROR = 0.5
MIN_LIMIT = -400.0
MAX_LIMIT = 0.0
HOME_OFFSET = 0.0
HOME_SEARCH_VEL = 50.0
HOME_LATCH_VEL = -5.0
HOME_SEQUENCE = 0
```

#### 7c81.hal (Key Components)

```hal
# Mesa 7c81 HAL file for IntuiGUI

# Load the real-time components
# Use the hm2_rpspi driver for the Mesa 7c81 board
loadrt hm2_rpspi config="spidev_path=/dev/spidev0.0"

# Load the base threading components
loadrt threads name1=servo-thread period1=1000000

# Add the board functions to the servo thread
addf hm2_7c81.0.read servo-thread
addf hm2_7c81.0.write servo-thread

# Configure stepgen for X axis (joint 0)
setp hm2_7c81.0.stepgen.00.dirsetup 5000
setp hm2_7c81.0.stepgen.00.dirhold 5000
setp hm2_7c81.0.stepgen.00.steplen 5000
setp hm2_7c81.0.stepgen.00.stepspace 5000
setp hm2_7c81.0.stepgen.00.position-scale 1000
setp hm2_7c81.0.stepgen.00.maxvel 100
setp hm2_7c81.0.stepgen.00.maxaccel 750
net x-pos-cmd joint.0.motor-pos-cmd => hm2_7c81.0.stepgen.00.position-cmd
net x-pos-fb hm2_7c81.0.stepgen.00.position-fb => joint.0.motor-pos-fb
net x-enable joint.0.amp-enable-out => hm2_7c81.0.stepgen.00.enable

# Configure stepgen for Z axis (joint 1)
setp hm2_7c81.0.stepgen.01.dirsetup 5000
setp hm2_7c81.0.stepgen.01.dirhold 5000
setp hm2_7c81.0.stepgen.01.steplen 5000
setp hm2_7c81.0.stepgen.01.stepspace 5000
setp hm2_7c81.0.stepgen.01.position-scale 1000
setp hm2_7c81.0.stepgen.01.maxvel 100
setp hm2_7c81.0.stepgen.01.maxaccel 750
net z-pos-cmd joint.1.motor-pos-cmd => hm2_7c81.0.stepgen.01.position-cmd
net z-pos-fb hm2_7c81.0.stepgen.01.position-fb => joint.1.motor-pos-fb
net z-enable joint.1.amp-enable-out => hm2_7c81.0.stepgen.01.enable

# Connect E-Stop and machine power signals
net estop-out <= iocontrol.0.user-enable-out
net estop-out => iocontrol.0.emc-enable-in

# Connect spindle control signals
net spindle-speed-cmd spindle.0.speed-out => hm2_7c81.0.pwmgen.00.value
net spindle-on spindle.0.on => hm2_7c81.0.pwmgen.00.enable
```

### Setup and Usage Instructions

1. Place these files in the IntuiGUI_Config directory
2. Make the scripts executable:
   ```
   chmod +x setup_mesa_7c81.sh
   chmod +x start_intuigui_7c81.sh
   ```
3. Run the setup script as root:
   ```
   sudo ./setup_mesa_7c81.sh
   ```
4. Reboot if prompted
5. Start LinuxCNC with the Mesa 7c81 configuration:
   ```
   ./start_intuigui_7c81.sh
   ```

### Customizing the Configuration

The minimal configuration provided above is for a basic 2-axis lathe (X and Z). To adapt this for different machine configurations:

1. Modify the `[TRAJ]` and `[KINS]` sections in 7c81.ini to match your machine's kinematics
2. Add or remove `[AXIS_*]` and `[JOINT_*]` sections as needed
3. Update the HAL file to configure the appropriate stepgen outputs for your axes
4. Adjust the scale values based on your stepper motor and drive microstepping settings

### Troubleshooting

- If communication with the Mesa 7c81 fails, ensure SPI is properly enabled
- Use `mesaflash --spi --addr /dev/spidev0.0 --device 7c81 --readhmid` to test communication
- Check connections between the Raspberry Pi and the Mesa card
- Verify that your drivers are receiving step/dir signals

## Other Solutions

[Additional solutions would be listed here]