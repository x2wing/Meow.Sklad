from PyQt5 import QtWebEngineWidgets


class MapViewPage(QtWebEngineWidgets.QWebEnginePage):
    """ Специальная страница, который ловит prompt из JavaScript страницы,
        и сохраняет его диапазон
     """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # текущие размеры
        self.last_bounds = [[0.0, 0.0], [0.0, 0.0]]

    def javaScriptPrompt(self, QUrl, msg, default):
        """ Ловим событие prompt """
        # пытаемся прочитать строку
        try:
            # парсим
            bounds = [float(b) for b in msg.split(',')]
            self.last_bounds[0][0] = bounds[0]
            self.last_bounds[0][1] = bounds[1]
            self.last_bounds[1][0] = bounds[2]
            self.last_bounds[1][1] = bounds[3]
        except Exception:
            pass

        return False, default
