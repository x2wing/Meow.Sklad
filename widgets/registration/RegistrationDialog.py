import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt


class RegistrationDialog(QtWidgets.QDialog):
    """ Окно регистрации (поставщик, перевозчик, заказчик) """
    def __init__(self, parent=None):
        super(RegistrationDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
        # Загрузка виджета
        self.ui = uic.loadUi('./widgets/registration/registration_dialog.ui', self)

        # Тип пользователя: 0 - поставщик, 1 - перевозчик, 2 - заказчик
        self.userType = 0
        # Количество хранилищ
        self.storagesCount = 1

        # Сигналы-слоты
        self.ui.rb_supplier.toggled.connect(self.set_supplier)
        self.ui.rb_transfer.toggled.connect(self.set_transfer)
        self.ui.rb_customer.toggled.connect(self.set_customer)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).pressed.connect(self.check_data)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).pressed.connect(self.reject)

    def set_supplier(self):
        self.userType = 0
        self.ui.lbl_counter.setText('Склады')

    def set_transfer(self):
        self.userType = 1
        self.ui.lbl_counter.setText('Гаражи')

    def set_customer(self):
        self.userType = 2
        self.ui.lbl_counter.setText('Магазины')

    def check_data(self):
        """ Проверка на ввод """
        if not self.ui.lne_name.text():
            return False
        if not self.ui.lne_address.text():
            return False

        super(RegistrationDialog, self).accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = RegistrationDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        print('accepted')
    else:
        print('rejected')

    sys.exit(app.exec_())
