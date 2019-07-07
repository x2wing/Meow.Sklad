import os
import sys
import random
from enum import Enum
from PyQt5 import QtWidgets, QtGui, uic

import db


class Users(Enum):
    """ Типы пользователей """
    Supplier = 0
    Transfer = 1
    Customer = 2


UsersNames = {
    Users.Supplier: 'Поставщик',
    Users.Transfer: 'Перевозчик',
    Users.Customer: 'Заказчик',
}


class ProductWidget(QtWidgets.QGroupBox):
    """ Виджет товара """
    def __init__(self, parent=None, data=None, image_path=None):
        super(ProductWidget, self).__init__(parent)
        if data is None:
            data = {
                'название': 'вода',
                'объём': 100,
                'единицы': 'литры',
            }
        # Загрузка виджета
        self.ui = uic.loadUi('widgets/cards/product_widget.ui', self)

        # Установка данных на виджете
        self.setTitle(data['название'])
        self.ui.spb_volume.setValue(float(data['объём']))
        self.ui.lne_units.setText(data['единицы'])

        if image_path is not None:
            image = QtGui.QPixmap(image_path).scaled(100, 100)
            self.ui.lbl_image.setPixmap(image)


class CardWidget(QtWidgets.QWidget):
    """ Окно информации о пользователе """
    def __init__(self, parent=None, data=None):
        super(CardWidget, self).__init__(parent)
        if data is None:
            data = {
                'name': 'Ufa',
                'type': Users.Supplier,
            }
        # Загрузка виджета
        self.ui = uic.loadUi('widgets/cards/card_widget.ui', self)
        # Установка данных
        self.ui.lne_name.setText(data['name'])
        self.ui.lne_type.setText(UsersNames[data['type']])
        # Виджет вывода каротчек продуктов
        self.wdg_products = QtWidgets.QWidget(self)
        self.products_layout = QtWidgets.QVBoxLayout(self.wdg_products)
        self.wdg_products.setLayout(self.products_layout)
        self.ui.sca_products.setWidget(self.wdg_products)

        # Поставщик
        if data['type'] == Users.Supplier:
            users_db = db.Suppliers()
        # Перевозчик
        elif data['type'] == Users.Transfer:
            users_db = db.Transfer()
        # Заказчик
        else:
            users_db = db.Customers()

        image_names = os.listdir('images/cats')
        user = list(users_db.get_by_name(data['name']))
        if user:
            user = user[0]
            print(user)

            # Установка данных из базы
            self.ui.lne_address.setText(user['адрес'])
            self.ui.spb_latitude.setValue(float(user['Координаты'][0]))
            self.ui.spb_longitude.setValue(float(user['Координаты'][1]))
            # Вывод продуктов
            for product in user['Требуемые товары']:
                self.wdg_products.layout().addWidget(
                    ProductWidget(
                        parent=self.wdg_products,
                        data={
                            'название': product,
                            'объём': user[product]['объём'],
                            'единицы': user[product]['единицы'],
                        },
                        image_path='images/cats/{0}'.format(image_names[random.randint(0, len(image_names) - 1)])
                    )
                )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = CardWidget()
    widget.show()
    sys.exit(app.exec_())
