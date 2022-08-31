import pyqtgraph as pg
import numpy as np


class graph_temperature(pg.PlotWidget):

    def __init__(self, object, parent=None, title='Temperature (ºc)', **kargs):
        super().__init__(parent=None, background='default', plotItem=None, **kargs)

        self.object = object
        self.ptr = 0
        self.temp_plot = self.object.plot(pen=(102, 252, 241), name='lol')
        self.object.setTitle(title)
        self.temp = np.linspace(0, 0, 30)


    def update(self, value):
        self.temp[:-1] = self.temp[1:]
        self.temp[-1] = float(value)
        # self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        self.ptr += 1
        self.temp_plot.setData(self.temp)
        self.temp_plot.setPos(self.ptr, 0)