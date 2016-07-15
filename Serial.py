import PyQt5.QtCore as QC
import PyQt5.QtSerialPort as QS
import PyQt5.QtWidgets as QW
import time

class SerialComm(QC.QObject):
    def __init__(self, data):
        super().__init__()
        self.info = QS.QSerialPortInfo()
        self.data = data
        self.speed = 115200
        self.port = None
        self.buffer = b""
        self.timer = QC.QTimer(self)
        self.timer.timeout.connect(self.internal_update)

    def list_ports(self):
        return self.info.availablePorts()

    def list_ports_as_text(self):
        return ["{} {} {}".format(port.portName(),
                                  port.manufacturer(),
                                  port.serialNumber())
                for port in self.list_ports()]

    def set_port(self, port):
        portlist = self.list_ports()
        if port >= 0 and port < len(portlist):
            self.port = QS.QSerialPort(portlist[port])
        else:
            self.port = None

    def connect(self):
        if self.port is None:
            return False
        if not (self.port.open(QC.QIODevice.ReadWrite)):
            raise SerialComm.InvalidSerial()
        self.port.setBaudRate(self.speed)
        self.port.readyRead.connect(self.internal_update)
        print("Port connected")
        self.start()
        return True

    def start(self):
        self.running = True

    def internal_update(self):
        bytesToRead = self.port.bytesAvailable()

        self.buffer += bytes(self.port.readAll())  # Data(bytesToRead)

        found = 1
        while found == 1:
            try:
                idx = self.buffer.index(b'\n')
                rawval = self.buffer[0:idx].strip()
                if b',' in rawval:
                    value = [float(i)
                             for i in rawval.split(b',')]
                else:

                    value = None

                self.buffer = self.buffer[idx+1:]
                found = 1
                if value is not None:
                    self.data.append(value)

            except ValueError:
                found = 0

        self.data.updated.emit()

    def stop(self):
        self.running = False
        self.port.close()

    class InvalidSerial(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                'Impossible to connect')


class DeviceWindow(QW.QDialog):
    def __init__(self, comm, parent=None):
        super().__init__(parent)
        self.comm = comm
        self.setMinimumWidth(500)
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QC.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QW.QDialogButtonBox.Cancel | QW.QDialogButtonBox.Ok)
        self.error = QW.QLabel('Error')
        self.label = QW.QLabel('List of devices found')
        self.portlist = QW.QListWidget(self)

        self.verticalLayout = QW.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.error)
        self.error.hide()
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.portlist)
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.rejected.connect(self.hide)
        self.buttonBox.accepted.connect(self.update_comm)

    def show(self):
        for item in range(0, self.portlist.count()):
            self.portlist.takeItem(item)
        for port in self.comm.list_ports_as_text():
            self.portlist.addItem(port)
        super().show()

    def update_comm(self):
        self.comm.set_port(self.portlist.currentRow())
        try:
            print("Trying to connect")
            self.comm.connect()
            self.error.hide()
            self.hide()
        except SerialComm.InvalidSerial:
            print("Error opening")
            self.error.show()
