from pyqtgraph.opengl import GLMeshItem, GLViewWidget, GLLinePlotItem, MeshData
import numpy as np
from stl import mesh

class graph_visualizer(GLViewWidget):
    def __init__(self, object, **kargs):
        super().__init__(parent=None,  **kargs)

        self.object = object

        stl_mesh = mesh.Mesh.from_file('rocket2.stl')
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        mesh_data = MeshData(vertexes=points, faces=faces)

        self.cube = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))

        axis_length = 2.0
        self.axis_x = GLLinePlotItem(pos=np.array([[0, 0, 0], [axis_length, 0, 0]]), color=(1, 0, 0, 1))
        self.axis_y = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, axis_length, 0]]), color=(0, 1, 0, 1))
        self.axis_z = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, axis_length]]), color=(0, 0, 1, 1))
