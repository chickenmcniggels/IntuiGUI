# IntuiCAM

**IntuiCAM** is a project developed for lathe machines with a special focus on providing an intuitive touchscreen interface in portrait mode. The goal is to deliver an easy-to-use control panel that integrates seamlessly with LinuxCNC systems.

> **Note:** This project is still in early development and is not fully functional yet. Feedback and contributions are welcome!

## Features (Planned)
- **Touchscreen Optimized:** Designed primarily for portrait mode displays.
- **Lathe Integration:** Tailored for lathe operations.
- **Modular Structure:** Files are organized for easy deployment and customization.

## Repository Structure

IntuiCAM/ # Repository root 
├── IntuiCAM_Screen/ # Screen files to be deployed to /usr/share/qtvcp/screens/ 
├── IntuiCAM_Config/ # Configuration files for LinuxCNC to be deployed to /home/cnc/linuxcnc/configs/ 
├── widgets/ # Contains touch_file_manager.py for /usr/lib/python3/dist-packages/qtvcp/widgets/ 
└── plugins/ # Contains simplewidgets_plugin.py for /usr/lib/python3/dist-packages/qtvcp/plugins/


Future Plans
Expand functionality and refine the interface.

Support additional machine types.

Enhance the touchscreen experience and add new features.

Contributing
Contributions are welcome! Please fork the repository and submit pull requests with your improvements.

License
This project is licensed under the MIT License.
