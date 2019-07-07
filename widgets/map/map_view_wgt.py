import folium

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets
from folium.plugins import MarkerCluster

from utils import popup_html_gen
from widgets.map.REST_HERE_MAP import hereTilesUrl
from widgets.map.map_view_page import MapViewPage

# ключ значение для доступа к сервису HERE
APP_ID = 'dGCxd2kAXscRgd6HfbWl'
APP_CODE = 'f2Rep5YTtS05GfvNFaxpfA'


def chain(gen1, gen2):
    """ Объединяем два генератора """
    yield from gen1
    yield from gen2


class MapView(QtWebEngineWidgets.QWebEngineView):
    """ Виджет который отображает одно веб-окно """

    reception_clicked = QtCore.pyqtSignal(object, object)  # supplier_name, reception_name
    garage_clicked = QtCore.pyqtSignal(object, object)  # customer_name, garage_name
    map_clicked = QtCore.pyqtSignal(object)  # coord

    def __init__(self, file_name="map.html", parent=None):
        super().__init__(parent)

        # сохраняем имя страницы
        self._file_name = file_name

        # список гаражей производителей
        self.garages = []  # список гаражей

        # зарегистрированные гаражи на карте
        self._garage_names_dict = {}

        # список пунктов приёма покупателей
        self.receptions = []  # список пунктов приёма

        # зарегистрированные пункты приёма на карте
        self._receptions_names_dict = {}

        # начальные координаты Уфы
        self._start_location = [54.7276, 55.9666]

        # формируем специальную страницу
        page = MapViewPage(self)
        self.setPage(page)
        page.map_clicked.connect(self._on_page_map_clicked)
        page.marker_clicked.connect(self._on_page_marker_clicked)

        # создаем страницу
        self._compile_map()

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

        # скртипт, который возвращает диапазоны при окончании движения карты
        js = """{map}.on('click', function(evt) 
            {{ prompt([evt.latlng.lat, evt.latlng.lng]) }} );""".format(map=m.get_name())
        # корневой объект html
        html = m.get_root()

        self._register_custom_js(html, js)

        # загружаем на карту гаражи
        self._load_garages_to(m)
        # загружаем на карту пункты приема
        self._load_receptions_to(m)

        # # подключаемся к ивентам маркеров
        # self._connect_to_js_markers(html)
        # сохраняем карту
        m.save(file_path)

        # загружаем в виджет страницу
        url = QtCore.QUrl.fromLocalFile(file_path)

        self.load(url)

    def _load_garages_to(self, map_, color='blue'):
        """ Отображаем на карте список сохраненных гаражей """

        for item in self.garages:
            marker = self._get_marker(item, color)
            # регистрируем маркер
            self._garage_names_dict[marker.get_name()] = item['Название']
            self.marker_cluster = MarkerCluster().add_to(map_)
            marker.add_to(self.marker_cluster)

    def _load_receptions_to(self, map_, color='red'):
        """ Отображаем на карте список сохраненных магазинов """
        for item in self.receptions:
            marker = self._get_marker(item, color)
            # регистрируем маркер
            self._receptions_names_dict[marker.get_name()] = item['Название']
            self.marker_cluster = MarkerCluster().add_to(map_)
            marker.add_to(self.marker_cluster)

    def _get_marker(self, item, color):

        popup = popup_html_gen(item)
        # popup = '<div>' + '<br><br><br>'.join([f"{k} : {v}" for k,v in item.items() if k!='Координаты' ]) + '</div>'
        return folium.CircleMarker([item['Координаты'][0], item['Координаты'][1]],
                             popup=popup, fill_color=color, color=color, fill_opacity=0.7)

    def _register_custom_js(self, html, js):
        """ Регистрируем кастомный скрипт на странице """
        e = folium.Element(js)
        html.script.get_root().render()
        # Insert new element or custom JS
        html.script._children[e.get_name()] = e

    def _connect_to_js_markers(self, html):
        """ Подключаемся к ивентам загружая скрипты на странице html """

        js_template = """{marker}.on('click', function(evt) 
            {{ prompt({marker}) }} );"""

        # проходим по всем маркерам
        for marker_js_name in chain(self._receptions_names_dict.keys(), self._garage_names_dict.keys()):
            # формируем и регистрируем новый скрипт
            js = js_template.format(marker=marker_js_name)
            self._register_custom_js(html, js)

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

    def _on_page_map_clicked(self, latlng):
        """ Действие при клике на карту """
        self.map_clicked.emit(latlng)

    def _on_page_marker_clicked(self, marker_name):
        """ Действие при клике на маркер """

        reception = self._receptions_names_dict.get(marker_name, None)
        if reception is not None:
            self.reception_clicked.emit(reception['supplier'], reception['reception'])
            return

        garage = self._garage_names_dict.get(marker_name, None)
        if garage is not None:
            self.garage_clicked.emit(garage['customer'], garage['garage'])
            return

        print("Marker " + marker_name + " not found")


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    web = MapView()  # QtWebEngineWidgets.QWebEngineView()

    web.show()
    app.exec()
