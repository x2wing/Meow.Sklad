from PyQt5 import QtCore, QtGui, QtWidgets
from widgets.map import MapView
from widgets.sign_in_dlg import SignInDlg
from widgets.registration import RegistrationDialog
from db import Suppliers, Customers


class MainWindow(QtWidgets.QMainWindow):
    """ Главное окно приложения """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(800, 500)

        # главный виджет карты
        self._map = MapView(parent=self)
        self.setCentralWidget(self._map)

        # добавим тулбар
        main_tb = QtWidgets.QToolBar(self)
        self._act_file = QtWidgets.QAction("Файл")

        # меню файл
        file_menu = QtWidgets.QMenu()

        # имя текущего пользователя
        self._current_user = None
        # Акшн который указывает на текущего пользователя
        self._user_act = QtWidgets.QAction("Войти")
        self._user_act.triggered.connect(self._on_user_act)
        file_menu.addAction(self._user_act)

        # Акшн для добавления нового пользовтеля
        self._register_act = QtWidgets.QAction("Зарегистрироваться")
        self._register_act.triggered.connect(self._on_reg_act)
        file_menu.addAction(self._register_act)

        # Акшн для выхода
        self._log_out_act = QtWidgets.QAction("Выйти из под пользователя ")
        self._log_out_act.triggered.connect(self._on_log_out_act)

        # Акшн для выхода из системы
        self._exit_act = QtWidgets.QAction("Выйти из системы")
        self._exit_act.triggered.connect(self._on_exit_act)
        file_menu.addAction(self._exit_act)

        self._act_file.setMenu(file_menu)

        main_tb.addAction(self._act_file)
        # меню для работы с БД

        self._db_act = QtWidgets.QAction("Работа с базой данных")
        db_menu = QtWidgets.QMenu()

        self._show_all_act = QtWidgets.QAction("Отобразить всё")
        self._show_all_act.triggered.connect(self._on_show_all)
        db_menu.addAction(self._show_all_act)

        self._show_my_receptions = QtWidgets.QAction("Отобразить мои склады")
        self._show_my_receptions.triggered.connect(self._on_show_my_receptions)
        db_menu.addAction(self._show_my_receptions)

        self._show_my_garages = QtWidgets.QAction("Отобразить мои гаражи")
        self._show_my_garages.triggered.connect(self._on_show_my_garages)
        db_menu.addAction(self._show_my_garages)

        self._clear_all_act = QtWidgets.QAction("Очистить всё")
        self._clear_all_act.triggered.connect(self._on_clear_all)
        db_menu.addAction(self._clear_all_act)

        self._db_act.setMenu(db_menu)
        main_tb.addAction(self._db_act)

        # добавим главный тулбар
        self.addToolBar(main_tb)
        self._update_user_act()

    def _on_user_act(self):
        """ Клик на акшн пользователя"""
        if self._current_user is None:
            # Открыть виджет для входа
            sign_in_dlg = SignInDlg(self)
            sign_in_dlg.show()
            ok = sign_in_dlg.exec()
            if ok:
                self._current_user = sign_in_dlg.comboUsername.currentText()
        else:
            # открыть виджет пользователя
            pass

        self._update_user_act()

    def _update_user_act(self):
        # обновляем акшн
        self._user_act.setText(self._current_user if self._current_user is not None else "Войти")
        self._log_out_act.setEnabled(self._current_user is not None)
        if self._current_user is not None:
            menu = QtWidgets.QMenu()
            self._user_act.setMenu(menu)
            menu.addAction(self._log_out_act)

            text = "Вы вошли под пользователем " + self._current_user
        else:
            self._user_act.setMenu(None)
            text = "Войдите или зарегистрируйтесь в системе"

        self.setWindowTitle("ЦИФРОВОЙ ПРОРЫВ 2019   " + text)

    def _on_reg_act(self):
        """ Клик на акшн зарегистрироваться """
        ok = True
        if self._current_user is not None:
            result = QtWidgets.QMessageBox.question(self, 'Вы пошли под пользователем' + self._current_user,
                                                    "Выйти?")
            if result == QtWidgets.QMessageBox.Yes:
                self._current_user = None
            else:
                ok = False

        # если регистрируемся
        if ok:
            reg_dlg = RegistrationDialog(self)
            reg_ok = reg_dlg.exec()
            if reg_ok == QtWidgets.QDialog.Accepted:
                self._current_user = reg_dlg.ui.lne_name.text()
                self._update_user_act()

    def _on_log_out_act(self):
        """ Клик на акшн выйти из под пользователя """
        ok = QtWidgets.QMessageBox.question(self,
                                            "Подтверждение",
                                            "Вы точно хотите выйти из под пользователя {user}?".format(user=self._current_user))
        if ok == QtWidgets.QMessageBox.Yes:
            self._current_user = None
            self._update_user_act()

    def _on_exit_act(self):
        """ Клик на акшн выход """
        ok = QtWidgets.QMessageBox.question(self,
                                            "Подтверждение выхода", "Вы точно хотите выйти?")
        if ok == QtWidgets.QMessageBox.Yes:
            self.close()

    def _on_show_all(self):
        """ Отобразить всё """
        # загружаем все склады
        self._map.receptions = Suppliers().get_all()
        # загружаем все гаражи
        self._map.garages = Customers().get_all()

        self._map.reload_slot()

    def _on_clear_all(self):
        """ Очистить карту """
        self._map.receptions = []
        self._map.garages = []
        self._map.reload_slot()

    def _on_show_my_receptions(self):

        self._map.receptions = Suppliers().get_by_name(self._current_user)
        self._map.garages = []
        self._map.reload_slot()

    def _on_show_my_garages(self):

        self._map.receptions = []
        self._map.garages = Customers().get_by_name(self._current_user)
        self._map.reload_slot()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
