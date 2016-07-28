import PyQt5.QtCore as QC
import numpy as np
import math
import csv
import time

class Data(QC.QObject):
    """The class handling the data"""
    updated = QC.pyqtSignal()
    NUM_CURVES = 2

    def __init__(self):
        self.buffer = b''
        self.data = [[] for i in range(0,self.NUM_CURVES)]
        self.ymin = 0
        self.ymax = 0
        self.time = []
        self.offset = None
        super().__init__()

    @property
    def xmin(self):
        return 0

    @property
    def xmax(self):
        return max(self.time)

    def append(self, data):
        if len(data) != self.NUM_CURVES:
            return False
        for channel in range(0, len(data)):
            if data[channel] < self.ymin:
                self.ymin = math.floor(data[channel])
            elif data[channel] > self.ymax:
                self.ymax = data[channel]

            self.data[channel] += [data[channel]]
        if self.offset is None:
            self.offset = time.time()
        self.time.append(time.time()-self.offset)

    def set_timer(self, timer):
        self.timer = timer

    def data_channel(self, channel):
        return np.array(self.data[channel])

    def time_channel(self):
        return np.array(self.time)

    def csv_data(self, ofile, headers=None):
        if headers is None:
            headers = []
        writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['Time']+ headers)
        for i in range(0,len(self.data[0])):
            writer.writerow([self.time[i], self.data[0][i], self.data[1][i]])
