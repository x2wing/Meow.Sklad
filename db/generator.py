# import requests
from pprint import pprint
from core import *
import geocoder
import geocoder
import contextlib


def fill_db(city):
    g = geocoder.arcgis(city)

    with contextlib.suppress( TypeError):
        data = {'адрес': g.json['address'],
            'Название': g.json['address'],
            'Координаты': [g.json['lat'], g.json['lng']],
            'Требуемые товары': ['хлеб', 'молоко', 'яйца'],
            'хлеб': {'объём': '30',
                     'единицы': 'литры'},
            'молоко': {'объём': '30',
                       'единицы': 'кг'},
            'яйца': {'объём': '30',
                     'единицы': 'м'}}

        supliers = Customers()
        supliers.set_supplier(data)
    # g = geocoder.yandex([55.95, 37.96], method='reverse')
        print(g.json['address'])
        print(g.json['lat'])
        print(g.json['lng'])


# pprint(g.json)
# results = r.json()['results']
# location = results[0]['geometry']['location']
# print(results)
# print(location['lat'], location['lng'])

if __name__ == '__main__':
    for city in open('city', 'rb'):
        print(city)
        fill_db(city)
