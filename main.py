import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from Graph import Canvas
from Data import Data
# from pyqtgraph.Qt import QtGui as QG

from Serial import SerialComm, DeviceWindow
from Config import Config, ConfigWindow

import numpy as np
from vispy import scene as vps

NUM_CURVES = 2
CURVE_COLOR = [[0.5, 0.5, 1, 1],
               [0.5, 1, 0.5, 1],
               [1, 0.5, 0.5, 1]]

# Add quit button
# Add saving data
# Add loading data
# Clean up interface

class Form(QW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auto_update = True
        self.to_update = False
        self.data = Data()
        self.config = Config()
        self.configwindow = ConfigWindow(self.config,
                                         self)
        self.serialcomm = SerialComm(self.data)
        self.devicewindow = DeviceWindow(self.serialcomm,
                                         self)
        self.automode = QW.QCheckBox("Auto scaling")
        self.automode.setCheckState(QC.Qt.Checked)
        self.startbutton = QW.QPushButton("Start")
        self.stopbutton = QW.QPushButton("Stop")
        self.resetaxis = QW.QPushButton("Reset axis")
        self.devicebutton = QW.QPushButton("Devices")
        self.configbutton = QW.QPushButton("Configuration")
        self.redraw_timer = QC.QTimer()
        
        buttonLayout1 = QW.QVBoxLayout()
        buttonLayout1.addWidget(self.startbutton)
        buttonLayout1.addWidget(self.stopbutton)
        self.startbutton.hide()
        self.stopbutton.hide()
        buttonLayout1.addWidget(self.automode)
        buttonLayout1.addWidget(self.resetaxis)
        buttonLayout1.addWidget(self.devicebutton)
        buttonLayout1.addWidget(self.configbutton)

        self.canvas = Canvas()
        self.canvas.canvas.events.mouse_wheel.connect(self.autooff)
        self.canvas.canvas.events.mouse_press.connect(self.autooff)

        for i in range(0, NUM_CURVES):
            self.canvas.lines.append(vps.visuals.Line(
                parent=self.canvas.viewbox.scene,
                color=CURVE_COLOR[i],
                method='gl',
                antialias=False))
        buttonLayout1.addWidget(self.canvas.canvas.native)
        self.canvas.canvas.show()
        self.resetaxis.clicked.connect(self.reset_range)
        self.automode.stateChanged.connect(self.autoswitch)
        self.devicebutton.clicked.connect(self.devicewindow.show)
        self.configbutton.clicked.connect(self.configwindow.show)
        self.serialcomm.started.connect(self.start)
        self.serialcomm.stoped.connect(self.stop)
        self.stopbutton.clicked.connect(self.serialcomm.stop)
        self.startbutton.clicked.connect(self.serialcomm.connect)
        self.data.updated.connect(self.update_figure)

        mainLayout = QW.QGridLayout()
        mainLayout.addLayout(buttonLayout1, 0, 1)
        self.redraw_timer.start(1000)
        self.redraw_timer.timeout.connect(self.internal_update_figure)
        self.setLayout(mainLayout)
        self.setWindowTitle("ArduGraph")

    def start(self):
        self.startbutton.hide()
        self.stopbutton.show()

    def stop(self):
        self.startbutton.show()
        self.stopbutton.hide()
        
    def autoswitch(self, signal):
        if signal == QC.Qt.Checked:
            self.auto_update = True
        else:
            self.auto_update = False

    def autooff(self, *args, **kwargs):
        print("Auto off")
        self.auto_update = False
        self.automode.setCheckState(QC.Qt.Unchecked)

    def update_figure(self):
        self.to_update = True

    def internal_update_figure(self):
        if self.to_update is False:
            return
        self.to_update = False
        xvals = list(range(0,self.data.xmax))
        for i in range(0, NUM_CURVES):
            self.canvas.lines[i].set_data(pos=np.rot90(np.array([xvals,
                                                                 self.data.data_channel(i)])))
        if self.auto_update:
            self.reset_range()
        #self.canvas.canvas.swap_buffers()

    def reset_range(self):
        self.canvas.viewbox.camera.set_range(x=[0, self.data.xmax],
                                             y=[self.data.ymin,
                                                self.data.ymax])

if __name__ == '__main__':
    import sys

    app = QW.QApplication(sys.argv)

    screen = Form()

    screen.show()

    sys.exit(app.exec_())
