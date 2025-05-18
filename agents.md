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