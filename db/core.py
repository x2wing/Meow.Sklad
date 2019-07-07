from bson import ObjectId
from pymongo import MongoClient

# import dnspython

DB_URI = 'mongodb+srv://rnbashnipineft:Qwe-1234@hackaton-avpwq.mongodb.net/test?retryWrites=true&w=majority'
filtred_keys = '_id', 'адрес', 'Название',  'Требуемые товары'

def get_db():
    """
    Configuration method to return db instance
    """

    db = MongoClient(
        DB_URI,
        # TODO: Connection Pooling
        maxPoolSize=50,
        # Set the maximum connection pool size to 50 active connections.
        # TODO: Timeouts
        # Set the write timeout limit to 2500 milliseconds.
        w="majority",
        wtimeout=2500,
    )["logistic"]
    return db


class DB_Base:
    def get_by_name(self, name):
        return self.collection.find({'Название': name})

    def set_supplier(self, data: dict):
        return self.collection.insert_one(data)

    def update_by_name(self, name: str, data: dict):
        return self.collection.update_one({'Название': name}, {'$set': data}, upsert=True)

    def get_coord_by_good(self, goods: list):
        return self.collection.find({'Категория': {'$in': goods}, }, {'Название':1,  'Координаты':1})
        #{'Название':1,  'Координаты':1}
        # return self.collection.find({'': name}, {'Координаты:': 1, '_id': 0})

    def get_data_by_good(self, good):
        """
         возвращает записи где есть поле good
        """
        return self.collection.find({good: {"$exists": True}, })

    def get(self, pipeline):
        """универсальная функция поиск через pipeline
        pipeline - [{"$match": {"Название": "Bryansk, Bryanskaya oblast'"}}]"""
        return self.collection.aggregate(pipeline, allowDiskUse=True)

    def get_all(self, filter={}):
        return self.collection.find({})

    def get_all_goods(self, filter={}):
        return self.collection.find(filter, {key:0 for key in filtred_keys})

    @property
    def col(self):
        return self.collection


class Customers(DB_Base):
    """{'адрес': g.json['address'],
            'Название': g.json['address'],
            'Координаты': [g.json['lat'], g.json['lng']],
            'Требуемые товары': ['хлеб', 'молоко', 'яйца'],
            'хлеб': {'объём': '30',
                     'единицы': 'литры'},
            'молоко': {'объём': '30',
                       'единицы': 'кг'},
            'яйца': {'объём': '30',
                     'единицы': 'м'}}"""

    def __init__(self):
        self.collection = get_db()['Покупатели']


class Suppliers(DB_Base):
    """{'адрес': g.json['address'],
            'Название': g.json['address'],
            'Координаты': [g.json['lat'], g.json['lng']],
            'Требуемые товары': ['хлеб', 'молоко', 'яйца'],
            'хлеб': {'объём': '30',
                     'единицы': 'литры'},
            'молоко': {'объём': '30',
                       'единицы': 'кг'},
            'яйца': {'объём': '30',
                     'единицы': 'м'}}"""

    def __init__(self):
        self.collection = get_db()['Поставщики']


class Transfer(DB_Base):
    """{
        'Название': "ООО Башшаражмонтаж"
        'Количество гаражей': 5
        }"""

    def __init__(self):
        self.collection = get_db()['Трансфер']


class Garages(DB_Base):
    """
            {'адрес':<адрес>
             'Название' :"ООО Башшаражмонтаж" #
             'Адрес': 'город улица'
            'Координаты':[22.44, 45.454]
             'Требуемые товары': [<товар 1>, <товар 2>, <товар 3>]
            <товар 1>: {объём: '30',
                        {единицы: 'литры'}
            <товар 2>: {объём: '30',
                        {единицы: 'кг'}
            <товар 2>: {объём: '30',
                        {единицы: 'м'}}
            }"""

    def __init__(self):
        self.collection = get_db()['Гаражи']


class Reception_point(DB_Base):
    """
        {'адрес':<адрес>
         'Название' <Название>
        'Координаты':[22.44, 45.454]
         'Требуемые товары': [<товар 1>, <товар 2>, <товар 3>]
        <товар 1>: {объём: '30',
                    {единицы: 'литры'}
        <товар 2>: {объём: '30',
                    {единицы: 'кг'}
        <товар 2>: {объём: '30',
                    {единицы: 'м'}}
        }"""

    def __init__(self):
        self.collection = get_db()['Пункты приёма']


class storage(DB_Base):
    def __init__(self):
        self.collection = get_db()['Гаражи']


"""Покупатели
    {'адрес':<адрес>
    'геодата':[22.44, 45.454]
     'Требуемые товары': [<товар 1>, <товар 2>, <товар 3>]
    <товар 1>: {объём: '30',
                {единицы: 'литры'}
    <товар 2>: {объём: '30',
                {единицы: 'кг'}
    <товар 2>: {объём: '30',
                {единицы: 'м'}}
    }"""

if __name__ == '__main__':
    supliers = Suppliers()
    #
    # data = {"Название": "ООО Башшаражмонтаж",
    #         'Адрес': 'г. Уфа, ул. Вологодская 78',
    #         'Геодата': [54.56565, 55.45454],
    #         'Категория': ['Конфеты', 'Печенье', 'торты'], }
    # print(list(supliers.get_coord_by_good(['Конфеты'])))
    # supliers.set_supplier({'Название': 'ООО башшаржмонтаж'})
    # db = supliers.update_supplier_by_name('ООО башшаржмонтаж', {'Название': "jkhdkhfk"})
    # for i in db['Покупатели'].find({}):
    #     print(i)

    # pipeline = [{"$match": {"Название": "Bryansk, Bryanskaya oblast'"}}]
    # supliers = Suppliers()
    # print(list(supliers.get(pipeline)))

    supliers.col.update_many({}, { '$rename': {'коты': 'молоко'} })
