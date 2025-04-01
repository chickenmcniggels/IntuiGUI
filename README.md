# IntuiCAM

IntuiCAM is an experimental project aimed at developing an intuitive touchscreen interface designed specifically for lathe machines. Currently, the project is **not functional yet** and is under active development. The focus is on delivering a user-friendly interface optimized for touchscreens operating in portrait mode.

## Features

- **Touchscreen Interface**  
  Optimized for portrait mode, providing a natural and efficient user experience on touchscreen displays.
  
- **Lathe-Specific Design**  
  Initially developed for lathe machines, with planned features tailored to the unique requirements of lathe control.

- **Modular Structure**  
  The repository is structured into modules for easy integration:
  - **IntuiCAM_Screen**: Files intended for installation at `/usr/share/qtvcp/screens/`
  - **IntuiCAM_Config**: Configuration files for LinuxCNC setups, to be installed at `/home/cnc/linuxcnc/configs/`
  - **touch_file_manager.py**: A Python module to be added to `/usr/lib/python3/dist-packages/qtvcp/widgets/`
  - **simplewidgets_plugin.py**: A plugin to replace the existing file at `/usr/lib/python3/dist-packages/qtvcp/plugins/`

## Repository Structure

