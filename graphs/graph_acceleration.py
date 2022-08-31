import pyqtgraph as pg
import numpy as np


class graph_acceleration(pg.PlotWidget):

    def __init__(self, object, parent=None, title='Accelerations (m/s²)', **kargs):
        super().__init__(parent=None, background='default', plotItem=None, **kargs)

        self.object = object

        self.object.hideAxis('bottom')
        # adding legend

        self.accX_plot = self.object.plot(pen=(102, 252, 241), name="X")
        self.accY_plot = self.object.plot(pen=(29, 185, 84), name="Y")
        self.accZ_plot = self.object.plot(pen=(203, 45, 111), name="Z")
        self.object.setTitle(title)
        self.addLegend()
        self.accX_data = np.linspace(0, 0)
        self.accY_data = np.linspace(0, 0)
        self.accZ_data = np.linspace(0, 0)
        self.ptr = 0


    def update(self, ax, ay, az):
        self.accX_data[:-1] = self.accX_data[1:]
        self.accY_data[:-1] = self.accY_data[1:]
        self.accZ_data[:-1] = self.accZ_data[1:]

        self.accX_data[-1] = float(ax)
        self.accY_data[-1] = float(ay)
        self.accZ_data[-1] = float(az)
        self.ptr += 1

        self.accX_plot.setData(self.accX_data)
        self.accY_plot.setData(self.accY_data)
        self.accZ_plot.setData(self.accZ_data)

        self.accX_plot.setPos(self.ptr, 0)
        self.accY_plot.setPos(self.ptr, 0)
        self.accZ_plot.setPos(self.ptr, 0)