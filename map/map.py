from PyQt5.QtCore import QIODevice, QTimer, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io
from jinja2 import Template

class Map(QWebEngineView):

    coordinate_changed = pyqtSignal(float, float)

    def __init__(self, object, parent=None, **kargs):
        super().__init__(parent=None, **kargs)

        self.object = object
        # change this to start map at your location
        coordinate = (25.996177612826184, -97.15445504615106)
        self.map = folium.Map(
            tiles='http://mt1.google.com/vt/lyrs=s&h1=p1Z&x={x}&y={y}&z={z}',
            name="Satellite Only",
            attr="Google Map",
            zoom_start=18,
            coordinate=coordinate,
        )
        folium.raster_layers.TileLayer(
            tiles="http://mt1.google.com/vt/lyrs=m&h1=p1Z&x={x}&y={y}&z={z}",
            name="Standard Roadmap",
            attr="Google Map",
        ).add_to(self.map)
        folium.raster_layers.TileLayer(
            tiles="http://mt1.google.com/vt/lyrs=y&h1=p1Z&x={x}&y={y}&z={z}",
            name="Hybrid",
            attr="Google Map",
        ).add_to(self.map)
        folium.LayerControl().add_to(self.map)
        # folium.Marker(coordinate).add_to(self.map)

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.object.setHtml(data.getvalue().decode())

    def add_marker(self, latitude, longitude):
        js = Template(
            """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 1,
                "stroke": true,
                "weight": 5,
                "zoom": 14,
            }
        ).addTo({{map}});
        """
        ).render(map=self.map.get_name(), latitude=latitude, longitude=longitude)
        self.object.page().runJavaScript(js)