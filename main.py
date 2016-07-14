import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
# from pyqtgraph.Qt import QtGui as QG

import serial
# import pyqtgraph as pg

from vispy import scene as vps


from vispy.scene import SceneCanvas
import numpy as np

NUM_CURVES = 2
CURVE_COLOR = [[0.5, 0.5, 1, 1],
               [0.5, 1, 0.5, 1],
               [1, 0.5, 0.5, 1]]


def on_resize(canvas, vb, event):
    vb.pos = 1, 1
    vb.size = (canvas.size[0] - 2, canvas.size[1] - 2)


class Data(QC.QObject):
    """The class handling the data, to store and give to matplotlib"""
    updated = QC.pyqtSignal()

    def __init__(self):
        self.buffer = b''
        self.data = []
        self.data = np.zeros((1, NUM_CURVES),
                             dtype=np.float32)
        self.max_points = 4 * 60 * 60 * 100  # 100 points a second for 4 hours
        self.increment = 102400
        self.connect()
        self.running = True
        super().__init__()

    @property
    def xmin(self):
        return 0

    @property
    def xmax(self):
        return self.data.shape[0]

    @property
    def ymin(self):
        print("Ymin is {}".format(np.min(self.data)))
        return np.min(self.data)

    @property
    def ymax(self):
        print("Ymax is {}".format(np.max(self.data)))
        return np.max(self.data)

    def update(self):
        if self.running is False:
            return

        if self.ser is None:
            self.connect()
            return

        try:
            self.internal_update()
        except OSError:
            print("Serial error")
            self.connect()
            # Serial isn't working
            pass

    def connect(self):
        try:
            self.ser = serial.Serial('/dev/ttyACM1', 9600, timeout=0.1)
        except serial.serialutil.SerialException:
            print("Connexion error")
            self.ser = None
            pass

    def internal_update(self):
        bytesToRead = self.ser.inWaiting()
        self.buffer += self.ser.read(bytesToRead)
        print("Buffer is now: {}".format(self.buffer))
        found = 1
        while found == 1:
            try:
                idx = self.buffer.index(b'\n')
                rawval = self.buffer[0:idx].strip()
                if b',' in rawval:
                    value = [float(i)
                             for i in rawval.split(b',')]
                else:
                    print("Invalid value: {}".format(rawval))
                    value = None
                print("Value: {}".format(value))
                self.buffer = self.buffer[idx+1:]
                found = 1
                if value is not None:
                    self.data = np.concatenate((self.data,
                                                np.array([value],
                                                         dtype=np.float32)))
                self.updated.emit()

            except ValueError:
                found = 0
                pass

    def data_channel(self, channel):
        length = self.xmax

        out = np.concatenate(
            (np.linspace(0, length-1, length).reshape(length, 1),
             self.data[:, channel].reshape(length, 1)),
            axis=1)
        return out

    def stop(self):
        self.running = False
data = Data()


class Form(QW.QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        nameLabel = QW.QLabel("Name:")
        self.nameLine = QW.QLineEdit()
        self.automode = QW.QPushButton("Auto scaling")
        self.stop = QW.QPushButton("Stop")
        self.resetaxis = QW.QPushButton("Reset axis")
        self.auto_update = True
        buttonLayout1 = QW.QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)
        buttonLayout1.addWidget(self.stop)
        buttonLayout1.addWidget(self.automode)
        buttonLayout1.addWidget(self.resetaxis)

        self.canvas_0 = SceneCanvas()
        self.win = self.canvas_0.native

        self.grid = self.canvas_0.central_widget.add_grid(spacing=0)

        self.viewbox = self.grid.add_view(row=0, col=1, camera='panzoom')

        # add some axes
        self.x_axis = vps.AxisWidget(orientation='bottom')
        self.x_axis.stretch = (1, 0.1)
        self.grid.add_widget(self.x_axis, row=1, col=1)
        self.x_axis.link_view(self.viewbox)
        self.y_axis = vps.AxisWidget(orientation='left')
        self.y_axis.stretch = (0.1, 1)
        self.grid.add_widget(self.y_axis, row=0, col=0)
        self.y_axis.link_view(self.viewbox)
        self.lines = []
        for i in range(0, NUM_CURVES):
            self.lines.append(vps.visuals.Line(parent=self.viewbox.scene))
        buttonLayout1.addWidget(self.win)
        self.canvas_0.show()
        self.canvas_0.events.mouse_wheel.connect(self.autooff)
        self.canvas_0.events.mouse_press.connect(self.autooff)
        self.resetaxis.clicked.connect(self.reset_range)
        self.automode.clicked.connect(self.autoswitch)
        self.stop.clicked.connect(data.stop)

        mainLayout = QW.QGridLayout()
        # mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addLayout(buttonLayout1, 0, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Hello Qt")

    def autoswitch(self):
        self.auto_update = True

    def autooff(self, *args, **kwargs):
        print("Auto off")
        self.auto_update = False

    def submitContact(self):
        name = self.nameLine.text()

        if name == "":
            QW.QMessageBox.information(self, "Empty Field",
                                       "Please enter a name and address.")
            return
        else:
            QW.QMessageBox.information(self, "Success!",
                                       "Hello %s!" % name)

    def update_figure(self):
        for i in range(0, NUM_CURVES):
            self.lines[i].set_data(pos=data.data_channel(i),
                                   color=CURVE_COLOR[i])
        if self.auto_update:
            self.reset_range()

    def reset_range(self):
        self.viewbox.camera.set_range(x=[0, data.xmax],
                                      y=[data.ymin, data.ymax])


if __name__ == '__main__':
    import sys

    app = QW.QApplication(sys.argv)

    # Simulating data arrival
    timer = QC.QTimer(app)
    timer.timeout.connect(data.update)
    timer.start(100)

    screen = Form()
    data.updated.connect(screen.update_figure)
    screen.show()

    sys.exit(app.exec_())
