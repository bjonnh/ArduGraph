import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import json


class InvalidConfig(Exception):
    def __init__(self, parameter):
        Exception.__init__(
            self,
            'Parameter {} is invalid'.format(parameter))


class ConfigModel(QC.QAbstractTableModel):
    def __init__(self, config):
        self.config = config
        self.data = {}
        super().__init__()

    def save(self):
        self.config.save()

    def headerData(self, section, orientation, role):
        if role == QC.Qt.DisplayRole:
            if orientation == QC.Qt.Vertical:
                return QC.QVariant(self.config.get_name(section))

    def flags(self, index):
        """Make only the values editable"""
        flags = super().flags(index)
        if index.column() == 0:
            return flags | QC.Qt.ItemIsEditable
        return flags

    def rowCount(self, parent):
        return len(self.config.data)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QC.QVariant()
        elif role != QC.Qt.DisplayRole:
            return QC.QVariant()
        return QC.QVariant(self.config.get(index.row()))

    def setData(self, index, value, role):
        if role == QC.Qt.EditRole:
            return self.config.set(index.row(), value)
        else:
            return False


class Config(QC.QObject):
    loaded = QC.pyqtSignal()

    def __init__(self, filename='config.json'):
        self.filename = filename
        self.parameters = ['channel1', 'channel2']
        self.defaultdata = {'channel1': 'Channel 1',
                            'channel2': 'Channel 2'}
        super().__init__()
        self.load()

    def get(self, row):
        if row >= len(self.parameters):
            return None
        else:
            return self.data[self.parameters[row]]

    def get_name(self, row):
        if row >= len(self.parameters):
            return None
        else:
            return self.parameters[row]

    def set(self, row, value):
        if row >= len(self.parameters):
            return False
        self.data[self.parameters[row]] = value
        return True

    def load(self):
        """Read the config file, store in self.data
        if file not found, use defaults"""
        try:
            with open(self.filename) as jsonfile:
                self.data = json.load(jsonfile)
                self.loaded.emit()
        except FileNotFoundError:
            self.data = self.defaultdata.copy()

    def save(self):
        """Write the config file, with data stored in self.data"""
        with open(self.filename, 'w') as jsonfile:
            json.dump(self.data, jsonfile)
            self.loaded = True


class ConfigWindow(QW.QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(500)
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QC.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QW.QDialogButtonBox.Cancel | QW.QDialogButtonBox.Ok)
        self.label = QW.QLabel('Configuration variables')
        self.error = QW.QLabel('Invalid parameter')

        self.paramlist = QW.QTableView(self)
        self.parammodel = ConfigModel(config)
        self.paramlist.setModel(self.parammodel)
        self.verticalLayout = QW.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.error)
        self.error.hide()
        self.verticalLayout.addWidget(self.paramlist)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.rejected.connect(self.hide)
        self.buttonBox.accepted.connect(self.done)

    def show(self):
        # Need to update from config
        self.error.hide()
        super().show()

    def done(self):
        try:
            self.parammodel.save()
            self.hide()
        except InvalidConfig as e:
            error = e.args
            self.error.setText(error)
            self.error.show()
