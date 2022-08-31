import pyqtgraph as pg
import numpy as np


class graph_altitude(pg.PlotWidget):

    def __init__(self, object, parent=None, title='Altitude (m)2', **kargs):
        super().__init__(parent=None, background='default', plotItem=None, **kargs)

        self.object = object
        self.ptr = 0
        self.alt_plot = self.object.plot(pen=(102, 252, 241), name='lol')
        self.object.setTitle(title)
        self.alt_data = np.linspace(0, 0, 30)


    def update(self, value):
        self.alt_data[:-1] = self.alt_data[1:]
        self.alt_data[-1] = float(value)
        # self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        self.ptr += 1
        self.alt_plot.setData(self.alt_data)
        self.alt_plot.setPos(self.ptr, 0)