#!/usr/bin/env python3
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView, QPushButton, QApplication, QFileSystemModel
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont
from qtvcp import logger
from qtvcp.core import Action, Status, Info

LOG = logger.getLogger(__name__)

# Create the global instances
STATUS = Status()
ACTION = Action()
INFO = Info()

class TouchFileManager(QWidget):
    """
    A touch-friendly FileManager that displays only G-code files and allows navigation
    within a given starting directory. It prevents navigating above the starting directory.
    When a file is double-clicked, it loads the file into LinuxCNC using ACTION.OPEN_PROGRAM.
    """
    def __init__(self, parent=None):
        super(TouchFileManager, self).__init__(parent)
        self.setWindowTitle("Touch File Manager")
        # Set the starting directory (adjust as needed)
        self.startingDir = os.path.expanduser("~/linuxcnc/nc_files")
        self.currentDir = self.startingDir
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        # Add a Back button for subfolder navigation
        self.backButton = QPushButton("Back")
        self.backButton.setFont(QFont("Lato Heavy", 24))
        self.backButton.setMinimumHeight(80)
        self.backButton.clicked.connect(self.goBack)
        mainLayout.addWidget(self.backButton)
        # Initially disable the back button since we are at the starting directory
        self.backButton.setEnabled(False)
        
        # Set up the file system model and filter to show only G-code files
        self.model = QFileSystemModel()
        self.model.setRootPath(self.startingDir)
        self.model.setNameFilters(["*.ngc", "*.nc", "*.tap"])
        self.model.setNameFilterDisables(False)
        
        # Set up the QListView
        self.listView = QListView()
        self.listView.setModel(self.model)
        self.listView.setRootIndex(self.model.index(self.currentDir))
        # Use a large touch-friendly font and disable alternating row colors (so all entries are the same)
        touchFont = QFont("Lato Heavy", 24)
        self.listView.setFont(touchFont)
        self.listView.setAlternatingRowColors(False)
        self.listView.setSelectionMode(QListView.SingleSelection)
        # Connect double-click signal to file/directory action
        self.listView.doubleClicked.connect(self.onFileDoubleClicked)
        mainLayout.addWidget(self.listView)

    def onFileDoubleClicked(self, index):
        """
        Called when an item is double-clicked.
        If it's a file, load it using ACTION.OPEN_PROGRAM.
        If it's a directory, navigate into it (provided it's under the starting directory).
        """
        path = self.model.filePath(index)
        if os.path.isfile(path):
            LOG.info("G-code file selected: " + path)
            self.loadFile(path)
        else:
            # Navigate into the directory if it is within the starting directory.
            normalizedStart = os.path.normpath(self.startingDir)
            normalizedPath = os.path.normpath(path)
            if normalizedPath.startswith(normalizedStart):
                self.currentDir = normalizedPath
                self.listView.setRootIndex(self.model.index(self.currentDir))
                LOG.info("Changed directory to: " + self.currentDir)
                # Enable the back button if we're no longer at the starting directory.
                self.backButton.setEnabled(self.currentDir != normalizedStart)
            else:
                LOG.info("Cannot navigate above the starting directory.")

    def loadFile(self, path):
        """
        Loads the selected file into LinuxCNC using ACTION.OPEN_PROGRAM
        and updates the machine log via STATUS.emit.
        """
        try:
            ACTION.OPEN_PROGRAM(path)
            STATUS.emit('update-machine-log', 'Loaded: ' + path, 'TIME')
            LOG.info("G-code file loaded successfully: " + path)
        except Exception as e:
            LOG.error("Error loading G-code file: {}".format(e))
            STATUS.emit('error', linuxcnc.NML_ERROR, "Load file error: {}".format(e))

    def goBack(self):
        """
        Navigates up one directory level, but not above the starting directory.
        """
        parentDir = os.path.dirname(self.currentDir)
        normalizedStart = os.path.normpath(self.startingDir)
        normalizedParent = os.path.normpath(parentDir)
        # Only navigate up if the parent directory is still within the starting directory.
        if normalizedParent.startswith(normalizedStart) and normalizedParent != normalizedStart:
            self.currentDir = normalizedParent
        else:
            self.currentDir = normalizedStart
        self.listView.setRootIndex(self.model.index(self.currentDir))
        LOG.info("Navigated up to: " + self.currentDir)
        self.backButton.setEnabled(self.currentDir != normalizedStart)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fm = TouchFileManager()
    fm.show()
    sys.exit(app.exec_())
