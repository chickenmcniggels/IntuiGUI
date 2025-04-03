IntuiGUI
IntuiGUI is an intuitive touchscreen interface designed specifically for lathe machines, aiming to provide seamless integration with LinuxCNC systems. This project emphasizes ease of use and is optimized for portrait mode displays.

Note: IntuiGUI is currently in early development stages and not yet fully functional. Contributions and feedback are highly encouraged!​

Planned Features
Touchscreen Optimization: Crafted for portrait-oriented displays to enhance user interaction.​

Lathe Machine Integration: Specifically tailored to accommodate lathe operations.​

Modular Architecture: Organized file structure to facilitate straightforward deployment and customization.​

Repository Structure
The repository is organized as follows:​

swift
Kopieren
Bearbeiten
IntuiGUI/                 # Repository root
├── IntuiGUI_Screen/      # Screen files for deployment to /usr/share/qtvcp/screens/
├── IntuiGUI_Config/      # LinuxCNC configuration files for /home/cnc/linuxcnc/configs/
├── widgets/              # Contains touch_file_manager.py for /usr/lib/python3/dist-packages/qtvcp/widgets/
└── plugins/              # Contains simplewidgets_plugin.py for /usr/lib/python3/dist-packages/qtvcp/plugins/
Future Plans
Expand functionality and refine the user interface.​

Extend support to additional machine types.​

Enhance the touchscreen experience with new features.​

Contributing
We welcome contributions! To contribute:​
GitHub

Fork the repository.​

Create a new branch for your feature or bug fix.​

Commit your changes with clear descriptions.​

Push your changes to your fork.​

Submit a pull request for review.​

Please ensure your contributions align with the project's goals and coding standards.​

License
This project is licensed under the MIT License. See the LICENSE file for more details.​

For more information and to access the repository, visit the IntuiGUI GitHub page.
