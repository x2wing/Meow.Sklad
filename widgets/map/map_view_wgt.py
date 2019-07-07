import folium

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets
from folium.plugins import MarkerCluster

from db import Suppliers
from widgets.map.REST_HERE_MAP import hereTilesUrl
from widgets.map.map_view_page import MapViewPage

# ключ значение для доступа к сервису HERE
APP_ID = 'dGCxd2kAXscRgd6HfbWl'
APP_CODE = 'f2Rep5YTtS05GfvNFaxpfA'


class MapView(QtWebEngineWidgets.QWebEngineView):
    """ Виджет который отображает одно веб-окно """

    def __init__(self, file_name="map.html", parent=None):
        super().__init__(parent)

        # сохраняем имя страницы
        self._file_name = file_name

        # список гаражей производителей
        self._garages = []  # список гаражей

        # список пунктов приёма покупателей
        self._receptions = []  # список пунктов приёма

        # начальные координаты Уфы
        self._start_location = [54.7276, 55.9666]

        # формируем специальную страницу
        page = MapViewPage(self)
        self.setPage(page)

        # создаем страницу
        self._compile_map()

        self.startTimer(100)

    def reload_slot(self):
        """ Действие на обновление страницы """

        self._compile_map()
        self.reload()

    def _compile_map(self):
        """ Формируем html-файл с отображением карты HERE """
        # файл, куда сохраняем страницу
        file_path = QtCore.QFileInfo(self._file_name).absoluteFilePath()

        # Tiles build
        tiles = hereTilesUrl(app_id=APP_ID, app_code=APP_CODE)
        # формируем карту
        m = folium.Map(location=self._start_location,
                       zoom_start=12,
                       tiles=tiles,
                       attr='here.com'
                       )
        marker_cluster = MarkerCluster().add_to(m)

        # скртипт, который возвращает диапазоны при окончании движения карты
        js = """{map}.on('moveend', function() 
            {{ var bounds = {map}.getBounds()
                prompt([bounds.getWest(), bounds.getEast(), 
                        bounds.getNorth(), bounds.getSouth()]) 
            
            }} );""".format(map=m.get_name())
        e = folium.Element(js)
        # корневой объект html
        html = m.get_root()
        html.script.get_root().render()
        # Insert new element or custom JS
        html.script._children[e.get_name()] = e

        # загружаем на карту гаражи
        self._load_garages_to(marker_cluster)
        # загружаем на карту пункты приема
        self._load_receptions_to(m)

        # сохраняем карту
        m.save(file_path)

        # загружаем в виджет страницу
        url = QtCore.QUrl.fromLocalFile(file_path)

        self.load(url)

    def _load_garages_to(self, map_):
        """ Отображаем на карте список сохраненных гаражей """
        tooltip = 'Click me!'

        for item in Suppliers().get_all_goods():
            popup = '<pre>' + '<p>'.join([f"{k} : {v}" for k,v in item.items() if k!='Координаты' ]) + '</pre>'
            folium.CircleMarker([item['Координаты'][0], item['Координаты'][1]],
                          popup=popup, color='red', fill_color='red').add_to(map_)

    def _load_receptions_to(self, map_):
        """ Отображаем на карте список сохраненных магазинов """
        pass

    def timerEvent(self, *args, **kwargs):
        pose = self.mapFromGlobal(QtGui.QCursor.pos())
        print(self.get_mouse_point(pose))

    def get_bounds(self):
        """ Возвращаем диапазон """
        return getattr(self.page(), "last_bounds", None)

    def get_mouse_point(self, screen_pos: QtCore.QPoint):
        """ Возвращает координаты точки """

        # запрашиваем размеры
        bounds = self.get_bounds()
        if bounds is not None:
            bound_width = bounds[0][1] - bounds[0][0]
            pose_x = bounds[0][0] + screen_pos.x() * bound_width / self.width()

            bound_height = bounds[1][1] - bounds[1][0]
            pose_y = bounds[1][0] + screen_pos.y() * bound_height / self.height()

            return pose_x, pose_y
        else:
            return None


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    web = MapView()  # QtWebEngineWidgets.QWebEngineView()

    web.show()
    app.exec()
