from PyQt5.QtWidgets import QDialog, QApplication, QGridLayout, QLineEdit, QComboBox, QLabel, QDialogButtonBox
from PyQt5 import QtCore

class SignInDlg(QDialog):
    """ Диалог входа в систему """

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        formGridLayout = QGridLayout(self)

        self.comboUsername = QComboBox(self)
        self.comboUsername.setEditable(True)

        self.editPassword = QLineEdit(self)
        self.editPassword.setEchoMode(QLineEdit.Password)

        labelUsername = QLabel(self)
        labelPassword = QLabel(self)
        labelUsername.setText("Логин")
        labelUsername.setBuddy(self.comboUsername)
        labelPassword.setText("Пароль")
        labelPassword.setBuddy(self.editPassword)

        buttons = QDialogButtonBox(self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok ).setText("Войти")
        buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        buttons.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        formGridLayout.addWidget(labelUsername, 0, 0)
        formGridLayout.addWidget(self.comboUsername, 0, 1)
        formGridLayout.addWidget(labelPassword, 1, 0)
        formGridLayout.addWidget(self.editPassword, 1, 1)
        formGridLayout.addWidget(buttons, 2, 0, 1, 2)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    d = SignInDlg()
    d.show()

    d.exec()
