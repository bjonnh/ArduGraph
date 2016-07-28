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
        self.savebutton = QW.QPushButton("Save")
        self.quitbutton = QW.QPushButton("Quit")
        self.redraw_timer = QC.QTimer()
        self.backup_timer = QC.QTimer()
        layout = QW.QVBoxLayout()        
        buttonLayout1 = QW.QHBoxLayout()
        buttonLayout1.addWidget(self.startbutton)
        buttonLayout1.addWidget(self.stopbutton)
        self.startbutton.hide()
        self.stopbutton.hide()
        buttonLayout1.addWidget(self.automode)
        buttonLayout1.addWidget(self.resetaxis)
        buttonLayout1.addWidget(self.devicebutton)
        buttonLayout1.addWidget(self.configbutton)
        buttonLayout1.addWidget(self.savebutton)
        buttonLayout1.addWidget(self.quitbutton)
        self.canvas = Canvas()
        self.canvas.canvas.events.mouse_wheel.connect(self.autooff)
        self.canvas.canvas.events.mouse_press.connect(self.autooff)

        for i in range(0, NUM_CURVES):
            self.canvas.lines.append(vps.visuals.Line(
                parent=self.canvas.viewbox.scene,
                color=CURVE_COLOR[i],
                method='gl',
                antialias=False))
        layout.addWidget(self.canvas.canvas.native)
        self.canvas.canvas.show()
        self.resetaxis.clicked.connect(self.reset_range)
        self.automode.stateChanged.connect(self.autoswitch)
        self.devicebutton.clicked.connect(self.devicewindow.show)
        self.configbutton.clicked.connect(self.configwindow.show)
        self.savebutton.clicked.connect(self.save)
        self.quitbutton.clicked.connect(self.quit)
        self.serialcomm.started.connect(self.start)
        self.serialcomm.stoped.connect(self.stop)
        self.serialcomm.disconnected.connect(self.disconnected)
        self.stopbutton.clicked.connect(self.serialcomm.stop)
        self.startbutton.clicked.connect(self.serialcomm.connect)
        self.data.updated.connect(self.update_figure)

        mainLayout = QW.QGridLayout()
        mainLayout.addLayout(buttonLayout1, 0, 1)
        mainLayout.addLayout(layout, 1, 1)
        self.redraw_timer.start(1000)
        self.backup_timer.start(30000)
        self.redraw_timer.timeout.connect(self.internal_update_figure)
        self.backup_timer.timeout.connect(self.tempsave)
        self.setLayout(mainLayout)
        self.setWindowTitle("ArduGraph")

    def quit(self):
        self.close()

    def save(self):
        filename = QW.QFileDialog.getSaveFileName(self, 'Save File', '.')
        fname = open(filename[0], 'w')
        self.data.csv_data(fname, self.config.headers())
        fname.close()

    def tempsave(self):
        fname = open("lastrun.csv", 'w')
        self.data.csv_data(fname, self.config.headers())
        fname.close()

    def start(self):
        self.startbutton.hide()
        self.stopbutton.show()

    def disconnected(self):
        self.startbutton.hide()
        self.stopbutton.hide()

    def stop(self):
        self.startbutton.show()
        self.stopbutton.hide()
        
    def autoswitch(self, signal):
        if signal == QC.Qt.Checked:
            self.auto_update = True
        else:
            self.auto_update = False

    def autooff(self, *args, **kwargs):
        self.auto_update = False
        self.automode.setCheckState(QC.Qt.Unchecked)

    def update_figure(self):
        self.to_update = True

    def internal_update_figure(self):
        if self.to_update is False:
            return
        self.to_update = False
        print(len(self.data.data_channel(0)))
        print(len(self.data.time_channel()))
        for i in range(0, NUM_CURVES):
            self.canvas.lines[i].set_data(pos=np.rot90(np.array([self.data.time_channel(),
                                                                 self.data.data_channel(i)])))
        if self.auto_update:
            self.reset_range()
        #self.canvas.canvas.swap_buffers()

    def reset_range(self):
        self.canvas.viewbox.camera.set_range(x=[0, self.data.xmax],
                                             y=[self.data.ymin,
                                                self.data.ymax])
    def closeEvent(self, event):
        event.ignore()
        if (QW.QMessageBox.Yes == QW.QMessageBox.question(
                self,
                "Do you want to exit?",
                "Are you sure you want to exit?",
                QW.QMessageBox.Yes|QW.QMessageBox.No
        )):
            event.accept()

if __name__ == '__main__':
    import sys

    app = QW.QApplication(sys.argv)

    screen = Form()

    screen.show()

    sys.exit(app.exec_())
