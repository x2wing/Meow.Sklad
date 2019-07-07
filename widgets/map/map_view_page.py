from PyQt5 import QtWebEngineWidgets, QtCore


class MapViewPage(QtWebEngineWidgets.QWebEnginePage):
    """ Специальная страница, который ловит prompt из JavaScript страницы,
        и сохраняет его диапазон
     """

    marker_clicked = QtCore.pyqtSignal(object)  # marker_name
    map_clicked = QtCore.pyqtSignal(object)  # coord

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # текущие размеры
        self.last_bounds = [[0.0, 0.0], [0.0, 0.0]]

    def javaScriptPrompt(self, QUrl, msg, default):
        """ Ловим событие prompt """

        print(msg)
        # парсим строку
        msg2 = [b for b in msg.split(',')]

        # пришло два аргумента - два числа
        if len(msg2) == 2:
            # посылаем сигнал о нажатии на карту
            try:
                latlng = [float(i) for i in msg2]
            except ValueError:
                latlng = None

            if latlng is not None:
                self.map_clicked.emit(latlng)
                return True, default

        # иначе пришло название маркера
        else:
            if msg2:
                self.marker_clicked.emit(msg2)
                return True, default

        return False, default
