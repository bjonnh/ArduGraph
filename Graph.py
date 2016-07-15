import PyQt5.QtCore as QC
from vispy.scene import SceneCanvas
from vispy import scene as vps


class Canvas(QC.QObject):
    def __init__(self):
        super().__init__()
        self.canvas = SceneCanvas()  # autoswap=False)
        self.grid = self.canvas.central_widget.add_grid(spacing=0)
        self.viewbox = self.grid.add_view(row=0, col=1, camera='panzoom')
        self.lines = []
        # add some axes
        self.x_axis = vps.AxisWidget(orientation='bottom')
        self.x_axis.stretch = (1, 0.1)
        self.grid.add_widget(self.x_axis, row=1, col=1)
        self.x_axis.link_view(self.viewbox)
        self.y_axis = vps.AxisWidget(orientation='left')
        self.y_axis.stretch = (0.1, 1)
        self.grid.add_widget(self.y_axis, row=0, col=0)
        self.y_axis.link_view(self.viewbox)
