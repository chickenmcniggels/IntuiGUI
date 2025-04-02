#####!/usr/bin/env python3
import sys
import os
import linuxcnc
import random  # For simulation dummy values

from PyQt5 import QtCore, QtWidgets, QtGui
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action, Info, Qhal
from qtvcp import logger
import hal
from qtvcp.lib.qt_vismach.qt_vismach import GLWidget, Capture, Collection, Box, CylinderZ, Color, Translate, HalRotate

LOG = logger.getLogger(__name__)

# Instantiate global libraries for keybindings, status, actions, etc.
KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()
INFO = Info()
QHAL = Qhal()


class HandlerClass:
    def __init__(self, halcomp, widgets, paths):
        self.hal = halcomp
        self.w = widgets
        self.PATHS = paths
        self.current_page = "homePage"
        self.axis_list = ["X", "Z", "Spindle"]
        self.axis_index = 0

        # Remove native window frame
        self.w.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # CAM Wizard step tracking (0-indexed for steps 1–5)
        self.current_cam_step = 0

        # Simulation timer reference
        self.simulationTimer = None

    def initialized__(self):
        """
        Called once the UI widgets and HAL pins are instantiated.
        Connect various buttons, set initial states, and embed the Vismach widget.
        """
        # --- Main Navigation ---
        self.w.btnControl.clicked.connect(lambda: self.showPage("controlPage"))
        self.w.btnCamWizard.clicked.connect(lambda: self.openCamWizard())
        self.w.btnTools.clicked.connect(lambda: self.showPage("toolsPage"))
        self.w.btnMakros.clicked.connect(lambda: self.showPage("makrosPage"))
        self.w.btnSettings.clicked.connect(lambda: self.showPage("settingsPage"))
        self.w.btnStatus.clicked.connect(self.goToStatusPage)
        self.w.btnStatus.setEnabled(self.isProgramRunning())
        self.w.btnHome.clicked.connect(lambda: self.showPage("homePage"))

        # --- CAM Wizard Connections ---
        self.w.btnStep1.clicked.connect(lambda: self.showCamStep(0))
        self.w.btnStep2.clicked.connect(lambda: self.showCamStep(1))
        self.w.btnStep3.clicked.connect(lambda: self.showCamStep(2))
        self.w.btnStep4.clicked.connect(lambda: self.showCamStep(3))
        self.w.btnStep5.clicked.connect(lambda: self.showCamStep(4))
        self.w.btnNextStep1.clicked.connect(lambda: self.advanceCamStep(1))
        self.w.btnPrevStep2.clicked.connect(lambda: self.advanceCamStep(-1))
        self.w.btnNextStep2.clicked.connect(lambda: self.advanceCamStep(1))
        self.w.btnPrevStep3.clicked.connect(lambda: self.advanceCamStep(-1))
        self.w.btnNextStep3.clicked.connect(lambda: self.advanceCamStep(1))
        self.w.btnPrevStep4.clicked.connect(lambda: self.advanceCamStep(-1))
        self.w.btnNextStep4.clicked.connect(lambda: self.advanceCamStep(1))
        self.w.btnPrevStep5.clicked.connect(lambda: self.advanceCamStep(-1))
        self.w.btnFinishCamWizard.clicked.connect(self.finishCamWizard)
        try:
            self.w.filemanager.fileDoubleClicked.connect(self.loadGCodeFile)
        except AttributeError:
            LOG.warning("FileManager does not have a 'fileDoubleClicked' signal; overriding load() method instead.")
            self.w.filemanager.load = self.loadGCodeFile

        # --- Control Page Connections ---
        self.w.btnRotateToolchanger.clicked.connect(self.rotateToolchanger)
        self.w.cmbJogIncrement.currentIndexChanged.connect(self.updateJogIncrement)
        self.w.btnAxisSelector.clicked.connect(self.selectAxis)

        # --- STATUS Signal Connections ---
        STATUS.connect('interp-run', self.on_program_start)
        STATUS.connect('interp-idle', self.on_program_stop)

        # --- Embed Vismach GLWidget into designated container ---
        container = self.w.findChild(QtWidgets.QWidget, "vismachWidget")
        if container:
            layout = container.layout()
            if layout is None:
                layout = QtWidgets.QVBoxLayout(container)
                container.setLayout(layout)
            self.glWidget = GLWidget(container)
            self.glWidget.set_latitudelimits(-180, 180)
            layout.addWidget(self.glWidget)

            # Create and initialize Capture objects
            world = Capture()
            world.capture()
            tooltip = Capture()
            tooltip.capture()
            work = Capture()
            work.capture()

            # Load the lathe model
            model = self.loadMachineModel()

            # Assign model with world capture as a Collection
            self.glWidget.model = Collection([model, world])
            self.glWidget.distance = 600 * 3
            self.glWidget.near = 600 * 0.01
            self.glWidget.far = 600 * 10.0

            try:
                self.glWidget.tool2view = tooltip
                self.glWidget.world2view = world
                self.glWidget.work2view = work
            except AttributeError:
                LOG.warning("GLWidget does not support one or more view properties (tool2view, world2view, work2view).")
        else:
            LOG.warning("vismachWidget container not found in UI.")

        LOG.info("IntuiGUI initialized; UI signals connected.")

    def loadGCodeFile(self):
        """
        Loads a GCode file from the FileManager widget.
        This method is triggered when the user double-clicks a file (or when the load method is called).
        """
        selection = self.w.filemanager.getCurrentSelected()
        if selection and selection[1]:
            gcode_path = selection[0]
            LOG.info("GCode file loaded: %s", gcode_path)
            self.gcodeFile = gcode_path  # Store the loaded file for later use
        else:
            LOG.warning("No valid GCode file selected.")

    def loadMachineModel(self):
        """
        Loads a lathe model using QtVismach primitives.
        This model includes a base, headstock, spindle, tailstock, tool post, and a workpiece.
        Modify dimensions as needed.
        """
        base = Box(-150, -50, 0, 150, 50, 20)
        base = Color([0.5, 0.5, 0.5, 1.0], [base])

        headstock = Box(-50, -30, 20, 50, 30, 60)
        headstock = Color([0.3, 0.3, 0.3, 1.0], [headstock])

        spindle = CylinderZ(0, 10, 100, 10)
        spindle = Color([0.8, 0.8, 0.8, 1.0], [spindle])
        spindle = HalRotate([spindle], None, "spindle.sim", 360, 0, 0, 1)

        tailstock = Box(100, -30, 20, 150, 30, 60)
        tailstock = Color([0.3, 0.3, 0.3, 1.0], [tailstock])

        tool_post = Box(60, -10, 60, 90, 10, 80)
        tool_post = Color([0.7, 0.7, 0.7, 1.0], [tool_post])

        workpiece = CylinderZ(0, 20, 300, 20)
        workpiece = Color([0.9, 0.9, 0.9, 1.0], [workpiece])
        workpiece = Translate([workpiece], 0, 0, 60)

        head_assembly = Collection([headstock, spindle, tool_post])
        lathe_model = Collection([base, head_assembly, tailstock, workpiece])
        LOG.info("Lathe model loaded: base, head assembly, tailstock, workpiece created.")
        return lathe_model

    def simulateGCode(self):
        """
        Simulates execution of loaded GCode by updating DRO displays and simulation state.
        Replace dummy values with actual simulation logic.
        """
        x = random.uniform(-100, 100)
        z = random.uniform(-50, 50)
        spindle_speed = random.uniform(0, 3000)
        try:
            self.w.droX.setText("{:.2f}".format(x))
            self.w.droZ.setText("{:.2f}".format(z))
            self.w.droSpindle.setText("{:.0f} RPM".format(spindle_speed))
        except AttributeError:
            LOG.warning("One or more DRO widgets not defined in UI.")
        if hasattr(self.glWidget, "updateSimulationState"):
            self.glWidget.updateSimulationState(x=x, z=z, spindle=spindle_speed)

    def startSimulation(self):
        """
        Starts a timer to update the simulation periodically.
        """
        self.simulationTimer = QtCore.QTimer()
        self.simulationTimer.timeout.connect(self.simulateGCode)
        self.simulationTimer.start(1000)
        LOG.info("Simulation timer started.")

    def stopSimulation(self):
        """
        Stops the simulation timer.
        """
        if self.simulationTimer:
            self.simulationTimer.stop()
            LOG.info("Simulation timer stopped.")

    # --- CAM Wizard Methods ---
    def openCamWizard(self):
        """
        Opens the CAM Wizard page and resets to step 1.
        """
        self.current_cam_step = 0
        self.showPage("camWizardPage")
        self.w.camWizardStack.setCurrentIndex(self.current_cam_step)
        self.updateCamWizardSideMenu()

    def showCamStep(self, step):
        """
        Jumps to a specific CAM Wizard step.
        """
        if 0 <= step < self.w.camWizardStack.count():
            self.current_cam_step = step
            self.w.camWizardStack.setCurrentIndex(step)
            self.updateCamWizardSideMenu()
            LOG.info("CAM Wizard jumped to step %d", step + 1)
            if step == 1:
                tools = self.processGCode()
                self.loadTools(tools)
            elif step == 2:
                zero = self.extractZeroPoint()
                LOG.info("Zero Point: %s", zero)
            elif step == 3:
                self.loadSimulation()

    def advanceCamStep(self, delta):
        """
        Advances (or goes back) one step in the CAM Wizard.
        """
        new_step = self.current_cam_step + delta
        if new_step < 0:
            new_step = 0
        elif new_step >= self.w.camWizardStack.count():
            new_step = self.w.camWizardStack.count() - 1
        self.current_cam_step = new_step
        self.w.camWizardStack.setCurrentIndex(new_step)
        self.updateCamWizardSideMenu()
        LOG.info("CAM Wizard advanced to step %d", new_step + 1)
        if new_step == 1:
            tools = self.processGCode()
            self.loadTools(tools)
        elif new_step == 2:
            zero = self.extractZeroPoint()
            LOG.info("Zero Point: %s", zero)
        elif new_step == 3:
            self.loadSimulation()

    def finishCamWizard(self):
        """
        Finishes the CAM Wizard, resets it for future use, and moves to the status page.
        """
        LOG.info("CAM Wizard finished. Resetting wizard and switching to status page.")
        self.current_cam_step = 0
        self.w.camWizardStack.setCurrentIndex(0)
        self.updateCamWizardSideMenu()
        self.showPage("statusPage")
        self.updateStatusButton()

    def updateCamWizardSideMenu(self):
        """
        Highlights the side menu buttons based on the current CAM Wizard step.
        Steps above: #3F7D20, current: #72B01D, steps below: #454955.
        """
        steps = [self.w.btnStep1, self.w.btnStep2, self.w.btnStep3, self.w.btnStep4, self.w.btnStep5]
        for i, btn in enumerate(steps):
            if i == self.current_cam_step:
                btn.setStyleSheet("background-color: #72B01D; color: white;")
            elif i < self.current_cam_step:
                btn.setStyleSheet("background-color: #3F7D20; color: white;")
            else:
                btn.setStyleSheet("background-color: #454955; color: white;")

    def processGCode(self):
        """
        Loads a GCode file (from a FileManager widget) and extracts tool information.
        Dummy implementation: returns a list of tool IDs.
        """
        try:
            gcode_file = self.w.filemanager.getFile()
        except AttributeError:
            gcode_file = "dummy.ngc"
        LOG.info("Loaded GCode file: %s", gcode_file)
        return [1, 2, 3]

    def loadTools(self, tools):
        """
        Loads extracted tool information into the machine toolchanger.
        Dummy implementation: stores the tool list.
        """
        LOG.info("Loading tools into toolchanger: %s", tools)
        self.tools = tools

    def extractZeroPoint(self):
        """
        Extracts the zero point from the GCode file.
        Dummy implementation returns (0,0,0).
        """
        LOG.info("Extracting Zero Point from GCode...")
        return (0.0, 0.0, 0.0)

    def loadSimulation(self):
        """
        Loads simulation paths for the GCode.
        Dummy implementation creates a random path.
        """
        LOG.info("Loading simulation of GCode paths...")
        path = [(random.uniform(-100, 100), random.uniform(-50, 50), random.uniform(0, 300)) for _ in range(20)]
        if hasattr(self.glWidget, "simulatePath"):
            self.glWidget.simulatePath(path)
        else:
            LOG.warning("GLWidget does not support simulatePath()")

    # --- STATUS Button Methods ---
    def updateStatusButton(self):
        """
        Enables the Status button if a program is running; otherwise disables it.
        """
        if self.isProgramRunning():
            self.w.btnStatus.setEnabled(True)
        else:
            self.w.btnStatus.setEnabled(False)

    def isProgramRunning(self):
        """
        Returns True if a program is running.
        Dummy implementation returns False.
        """
        return False

    def goToStatusPage(self):
        """
        Switches to the Status page if a program is running.
        """
        if self.isProgramRunning():
            LOG.info("Program is running. Switching to status page.")
            self.showPage("statusPage")
        else:
            LOG.info("No program running; Status button remains disabled.")

    def on_program_start(self, state, **kwargs):
        self.w.btnStatus.setEnabled(True)

    def on_program_stop(self, state, **kwargs):
        self.w.btnStatus.setEnabled(False)

    def showPage(self, pageName):
        """
        Switches the displayed page in the main QStackedWidget by matching the objectName.
        """
        for i in range(self.w.stackedWidget.count()):
            widget = self.w.stackedWidget.widget(i)
            if widget.objectName() == pageName:
                self.w.stackedWidget.setCurrentIndex(i)
                LOG.debug("Switched to page: %s", pageName)
                return

    # --- Control Page Functions (Lathe Manual Control) ---
    def jogAxis(self, axis, direction):
        LOG.info("Jogging axis %s in %s direction", axis, "positive" if direction > 0 else "negative")
        # Placeholder for ACTION.JOG command
        pass

    def changeSpindleSpeed(self, value):
        LOG.info("Changing spindle speed to: %s RPM", value)
        # Placeholder for ACTION.SET_SPINDLE_SPEED command
        pass

    def updateDRO(self):
        # Placeholder: update DRO widgets with current simulated values.
        pass

    def measureLaser(self):
        LOG.info("Laser micrometer measurement triggered.")
        measured_diameter = 50.0  # Dummy value
        try:
            self.w.droLaser.setText("{:.2f} mm".format(measured_diameter))
        except AttributeError:
            LOG.warning("droLaser widget not defined in UI.")

    def rotateToolchanger(self):
        LOG.info("Rotate Toolchanger pressed.")
        try:
            ACTION.RUN_TOOLCHANGER_ROTATION()
        except Exception as e:
            LOG.error("Toolchanger rotation command failed: %s", e)

    def updateJogIncrement(self, index):
        increment_str = self.w.cmbJogIncrement.itemText(index)
        try:
            increment = float(increment_str)
            LOG.info("Jog increment updated to: %s", increment)
        except Exception as e:
            LOG.error("Error updating jog increment: %s", e)

    def selectAxis(self):
        axis = self.getNextAxis()
        LOG.info("Axis selected: %s", axis)
        self.w.lblDRO_X.setText("X: 0.00 (Axis: {})".format(axis))

    def getNextAxis(self):
        axis = self.axis_list[self.axis_index]
        self.axis_index = (self.axis_index + 1) % len(self.axis_list)
        return axis

    def processed_key_event__(self, receiver, event, is_pressed, key, code, shift, cntrl):
        try:
            return KEYBIND.call(self, event, is_pressed, shift, cntrl)
        except Exception as e:
            LOG.error("Keybinding error: %s", e)
            return False

    def kb_jog(self, state, joint, direction, fast=False, linear=True):
        if not STATUS.is_man_mode() or not STATUS.machine_is_on():
            return
        if linear:
            distance = STATUS.get_jog_increment()
            rate = STATUS.get_jograte() / 60
        else:
            distance = STATUS.get_jog_increment_angular()
            rate = STATUS.get_jograte_angular() / 60
        if state:
            if fast:
                rate *= 2
            ACTION.JOG(joint, direction, rate, distance)
        else:
            ACTION.JOG(joint, 0, 0, 0)

    # --- Key Binding Callback Methods ---
    def on_keycall_ESTOP(self, event, state, shift, cntrl):
        if state:
            ACTION.SET_ESTOP_STATE(STATUS.estop_is_clear())

    def on_keycall_POWER(self, event, state, shift, cntrl):
        if state:
            ACTION.SET_MACHINE_STATE(not STATUS.machine_is_on())

    def on_keycall_HOME(self, event, state, shift, cntrl):
        if state:
            if STATUS.is_all_homed():
                ACTION.SET_MACHINE_UNHOMED(-1)
            else:
                ACTION.SET_MACHINE_HOMING(-1)

    def on_keycall_ABORT(self, event, state, shift, cntrl):
        if state:
            if STATUS.stat.interp_state == linuxcnc.INTERP_IDLE:
                self.w.close()
            else:
                ACTION.ABORT()

    def on_keycall_F12(self, event, state, shift, cntrl):
        if state:
            STYLEEDITOR.load_dialog()

    def on_keycall_XPOS(self, event, state, shift, cntrl):
        self.kb_jog(state, 0, 1, shift)

    def on_keycall_XNEG(self, event, state, shift, cntrl):
        self.kb_jog(state, 0, -1, shift)

    def on_keycall_YPOS(self, event, state, shift, cntrl):
        self.kb_jog(state, 1, 1, shift)

    def on_keycall_YNEG(self, event, state, shift, cntrl):
        self.kb_jog(state, 1, -1, shift)

    def on_keycall_ZPOS(self, event, state, shift, cntrl):
        self.kb_jog(state, 2, 1, shift)

    def on_keycall_ZNEG(self, event, state, shift, cntrl):
        self.kb_jog(state, 2, -1, shift)

    def on_keycall_APOS(self, event, state, shift, cntrl):
        if 'A' in INFO.AVAILABLE_AXES:
            self.kb_jog(state, 3, 1, shift, False)

    def on_keycall_ANEG(self, event, state, shift, cntrl):
        if 'A' in INFO.AVAILABLE_AXES:
            self.kb_jog(state, 3, -1, shift, linear=False)

    def closing_cleanup__(self):
        if self.w.PREFS_:
            self.w.PREFS_.putpref('DRO_Font', self.w.dro_label_1.font().toString(), str, 'CUSTOM_FORM_ENTRIES')
            color = self.w.dro_label_1.palette().color(QtGui.QPalette.Foreground).name()
            self.w.PREFS_.putpref('DRO_Color', color, str, 'CUSTOM_FORM_ENTRIES')
        self.stopSimulation()
        LOG.info("IntuiGUI closing cleanup called.")

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)


def get_handlers(halcomp, widgets, paths):
    """
    This function is called by QtVCP to retrieve the list of handlers.
    """
    return [HandlerClass(halcomp, widgets, paths)]
