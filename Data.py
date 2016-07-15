import PyQt5.QtCore as QC
import numpy as np


class Data(QC.QObject):
    """The class handling the data, to store and give to matplotlib"""
    updated = QC.pyqtSignal()
    NUM_CURVES = 2

    def __init__(self):
        self.buffer = b''
        self.data = [[]]*self.NUM_CURVES
        self.ymin = 0
        self.ymax = 0
        super().__init__()

    @property
    def xmin(self):
        return 0

    @property
    def xmax(self):
        return len(self.data[0])

    def append(self, data):
        if len(data) != self.NUM_CURVES:
            return False
        for channel in range(0, len(data)):
            if data[channel] < self.ymin:
                self.ymin = data[channel]
            elif data[channel] > self.ymax:
                self.ymax = data[channel]

            self.data[channel] += [data[channel]]

    def set_timer(self, timer):
        self.timer = timer

    def data_channel(self, channel):
        length = self.xmax

        out = np.array(self.data[channel])

        return out
