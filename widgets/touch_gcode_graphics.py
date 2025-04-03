#!/usr/bin/env python3

#Touch-enabled G-code Graphic Backplot Widget
#
#This widget builds upon the Lcnc_3dGraphics (which in turn uses QGLWidget)
#and adds:
#  - Pinch gesture to zoom (and rotate around the Z-axis)
#  - Two-finger swipe gesture to simulate right-mouse-button drag for pan/tilt/roll (rotate)
#  - Double-click (or double-tap) to reset the view to its original settings
#  - Only basic mouse handling (mode 0) is kept – the extra modes and DRO/HUD features
#    have been removed.
#
#File-loading, status handling and gcode processing remain intact.

import sys
import os
import gcode
import linuxcnc

from PyQt5.QtCore import pyqtProperty, QTimer, Qt, QEvent, QPointF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
# Note: QPinchGesture and QPanGesture types are used via the Qt gesture framework.

from qt5_graphics import Lcnc_3dGraphics
from qtvcp.widgets.widget_baseclass import _HalWidgetBase
from qtvcp.core import Status, Info
from qtvcp import logger

# Global objects for status and logging
STATUS = Status()
INFO = Info()
LOG = logger.getLogger(__name__)


class TouchGCodeGraphics(Lcnc_3dGraphics, _HalWidgetBase):
    def __init__(self, parent=None):
        super(TouchGCodeGraphics, self).__init__(parent)

        # Remove DRO/HUD related initialization; we only keep the file loading and graphics parts.
        self.colors['back'] = (0.0, 0.0, 0.75)  # original background color

        # Enable touch events and register gesture recognizers
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.grabGesture(Qt.PinchGesture)
        self.grabGesture(Qt.PanGesture)

        # For simplicity, fix the mouse mode to basic (mode 0) and remove extra modes.
        self._mouseMode = 0
        self._view_incr = 20  # for any view adjustments from external signals

        # Record initial view settings after GL is initialized.
        self._initialViewSettings = None

        # For simulating right-mouse drag (rotation control)
        self._simulatedRotatePos = None

    def initializeGL(self):
        # Call parent's initializeGL to set up OpenGL and the view.
        super(TouchGCodeGraphics, self).initializeGL()
        # Once the GL scene is ready, record the initial view settings.
        self._initialViewSettings = self.getCurrentViewSettings()

    def event(self, event):
        # Intercept gesture events.
        if event.type() == QEvent.Gesture:
            return self.gestureEvent(event)
        return super(TouchGCodeGraphics, self).event(event)

    def gestureEvent(self, event):
        # Handle pinch (zoom and rotation about Z) and two-finger swipe for rotation.
        pinch = event.gesture(Qt.PinchGesture)
        if pinch:
            self.handlePinchGesture(pinch)
        pan = event.gesture(Qt.PanGesture)
        if pan:
            self.handleRotateGesture(pan)
        return True

    def handlePinchGesture(self, gesture):
        if gesture.state() == Qt.GestureStarted:
            self._initialZoom = self.distance    # store current zoom level
            self._initialZRot = self.zRot         # store current Z-rotation
        elif gesture.state() == Qt.GestureUpdated:
            # Use totalScaleFactor for cumulative zoom change.
            newZoom = self._initialZoom / gesture.totalScaleFactor()
            self.setZoom(newZoom * 100)
            # Update rotation around Z-axis.
            newZRot = self._initialZRot + int(gesture.totalRotationAngle() * 16)
            self.setZRotation(newZRot)

    def handleRotateGesture(self, gesture):
        """
        Simulate right-mouse-button drag for rotation (pan, tilt, and roll).
        This uses a two-finger swipe gesture (QPanGesture) to call the same control as a right-mouse drag.
        """
        if gesture.state() == Qt.GestureStarted:
            # Initialize the simulated pointer position to the widget's center.
            self._simulatedRotatePos = QPointF(self.width() / 2, self.height() / 2)
            self.set_prime(self._simulatedRotatePos.x(), self._simulatedRotatePos.y())
        elif gesture.state() == Qt.GestureUpdated:
            # Update simulated position using the gesture's delta.
            delta = gesture.delta()  # incremental QPointF movement
            self._simulatedRotatePos += delta
            # Simulate right-mouse drag: call set_prime() and rotateOrTranslate() with the new position.
            self.set_prime(self._simulatedRotatePos.x(), self._simulatedRotatePos.y())
            self.rotateOrTranslate(self._simulatedRotatePos.x(), self._simulatedRotatePos.y())
            self.updateGL()

    def mouseDoubleClickEvent(self, event):
        """
        Reset the view to the initial recorded view settings when the widget is double-clicked.
        """
        if self._initialViewSettings:
            self.setRecordedView()
        event.accept()

    def wheelEvent(self, event):
        """
        Use the mouse wheel to zoom in or out (basic mode 0 functionality).
        """
        a = event.angleDelta().y() / 200
        if a < 0:
            self.zoomout()
        else:
            self.zoomin()
        event.accept()

    # --- File Loading and Status Signal Functions (kept intact) ---
    def addTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll)
        self.timer.start(INFO.GRAPHICS_CYCLE_TIME)

    def _hal_init(self):
        self._block_autoLoad = STATUS.connect('file-loaded', self.load_program)
        self._block_reLoad = STATUS.connect('reload-display', self.reloadfile)
        STATUS.connect('actual-spindle-speed-changed', self.set_spindle_speed)
        STATUS.connect('metric-mode-changed', lambda w, f: self.set_metric_units(w, f))
        self._block_viewChanged = STATUS.connect('graphics-view-changed',
                                                 lambda w, v, a: self.set_view_signal(v, a))
        self._block_lineSelect = STATUS.connect('gcode-line-selected',
                                                lambda w, l: self.highlight_graphics(l))

    def _hal_cleanup(self):
        if self.PREFS_:
            v, z, x, y, lat, lon = self.getRecordedViewSettings()
            LOG.debug('Saving {} data to file.'.format(self.HAL_NAME_))
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-view', v, str, 'SCREEN_CONTROL_LAST_SETTING')
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-zoom', z, float, 'SCREEN_CONTROL_LAST_SETTING')
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-panx', x, float, 'SCREEN_CONTROL_LAST_SETTING')
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-pany', y, float, 'SCREEN_CONTROL_LAST_SETTING')
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-lat', lat, float, 'SCREEN_CONTROL_LAST_SETTING')
            self.PREFS_.putpref(self.HAL_NAME_ + '-user-lon', lon, float, 'SCREEN_CONTROL_LAST_SETTING')

    def load_program(self, g, fname):
        LOG.debug('Loading display from file: {}'.format(fname))
        self._reload_filename = fname
        self.load(fname)
        STATUS.emit('graphics-gcode-properties', self.gcode_properties)
        self.set_current_view()

    def reloadfile(self, w):
        LOG.debug('Reloading display: {}'.format(self._reload_filename))
        try:
            self.load(self._reload_filename)
            self.clear_live_plotter()
            STATUS.emit('graphics-gcode-properties', self.gcode_properties)
        except Exception as e:
            LOG.error('Error reloading file {}: {}'.format(self._reload_filename, e))
            pass

    def set_spindle_speed(self, w, rate):
        if rate < 1:
            rate = 1
        self.spindle_speed = rate

    def set_metric_units(self, w, state):
        self.metric_units = state
        self.updateGL()

    def set_view_signal(self, view, args):
        v = view.lower()
        if v == 'clear':
            self.clear_live_plotter()
        elif v == 'zoom-in':
            self.zoomin()
        elif v == 'zoom-out':
            self.zoomout()
        elif v == 'pan-down':
            self.panView(self._view_incr, 0)
        elif v == 'pan-up':
            self.panView(-self._view_incr, 0)
        elif v == 'pan-right':
            self.panView(0, self._view_incr)
        elif v == 'pan-left':
            self.panView(0, -self._view_incr)
        elif v == 'rotate-ccw':
            self.rotateOrTranslate(self._view_incr, 0)
        elif v == 'rotate-cw':
            self.rotateOrTranslate(-self._view_incr, 0)
        elif v == 'rotate-up':
            self.rotateOrTranslate(0, self._view_incr)
        elif v == 'rotate-down':
            self.rotateOrTranslate(0, -self._view_incr)
        elif v == 'record-view':
            self.recordCurrentViewSettings()
        elif v == 'set-recorded-view':
            self.setRecordedView()
        else:
            self.set_view(v)

    def highlight_graphics(self, line):
        if self._current_file is None:
            return
        self.set_highlight_line(line)
        STATUS.emit('graphics-line-selected', line)

    def update_highlight_variable(self, line):
        self.highlight_line = line
        if line is None:
            line = -1
        STATUS.emit('graphics-line-selected', line)

    # --- End of File Loading / Status Functions ---

# --- For testing purposes only ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TouchGCodeGraphics()
    widget.show()
    sys.exit(app.exec_())
