##################################################################################################
# ************ОСНОВНЫЕ ЗАТРАТЫ ВРЕМЕНИ НА ОТКРЫТИЕ ЗАКРЫТИЕ ФАЙЛОВ*********************************
# ************ЛЮБЫМИ ПУТЯМИ УСТРАНЯЕМ ОТКРЫТИЕ, СОЗДАНИЕ И ЗАКРЫТИЕ ФАЙЛОВ*************************
# *************************База отдает и пишет быстро**********************************************
# Файл 49 МБ
# ВРЕМЯ ВЫПОЛНЕНИЯ upload 7.619637489318848
# ВРЕМЯ ВЫПОЛНЕНИЯ download 4.440134286880493
# Проект 2 Gb() normalize_new.h5geo (3).h5geo:
# ВРЕМЯ ВЫПОЛНЕНИЯ upload 724.848 seconds
# Файл 61 Gb big_test.h5geo:
# ВРЕМЯ ВЫПОЛНЕНИЯ upload 1717.058 seconds
##################################################################################################
from gridfs import GridFS, GridFSBucket
from pymongo import MongoClient
from bson.objectid import ObjectId
import h5py
import io

import shutil
import bson
import tempfile

from plugins.geosim.database.db_static import timer, h5_simple_copy

# ограничение bson
CHUNK_SIZE = 15 * 1024 * 1024
# temp_path = 'obj' - работает медленно т.к. надо создавать порядка 200 000 файлов на проект
# temp_path = io.BytesIO() # работае прекрасно только много памяти
temp_path = tempfile.SpooledTemporaryFile(max_size=CHUNK_SIZE * 4)

# параметры конфигурации
config_params = dict(host='localhosst', port=27017, username=None, password=None)
# название базы
database = 'Приобское'


class DBMongoBase:
    """лайтовый класс для получения списков (например списка всех проектов)"""

    def __init__(self, config_params):
        self.client = MongoClient(**config_params)

    def init_main(self):
        main_db_name = 'main'
        collection = 'projects'
        self.key_project_name = "project_name"
        self.collection = self.client[main_db_name][collection]

    def get_projects_list(self):
        self.init_main()
        return self.collection.find({},
                                    {'_id': 0, self.key_project_name: 1},
                                    no_cursor_timeout=True).distinct(self.key_project_name)


class DB_GridFS(DBMongoBase):
    """Класс работы с MongoDB Gridfs    """

    def __init__(self, config_params, database):
        """Получаем базу, GridFSBucket, коллекцию
        :param config_params: dict
            словарь конфигурационных парметров
            dict(host='10.205.33.221', port=27017, username=None, password=None)
        :param database: string
            название базы данных MongoDB
        """
        # Client for a MongoDB instance
        # client = MongoClient(**config_params)
        super().__init__(config_params)
        # print(self.client.test_database)
        # Get a database by client and name
        self.db = self.client[database]
        # получаем GridFSBucket
        self.fs = GridFSBucket(self.db)
        # получаем коллекцию fs.files - стандартная коллекция GridFSBucket
        self.collection = self.db.fs.files
        print(self.collection)
        self.meta = self.client['main'].projects
        print(self.meta)

    def upload(self, obj_name, filepath, metadata={'origin_hash': '_hash'}):
        """метод загрузки данных в БД
        :param obj_name: string
            название объекта value поля filename
        :param filepath: file_object
            file_object с данными, отправляемыми в БД
        :param metadata: dict
            метаданные записываемые в БД
        return: None
        """
        # GridIn instance
        grid_in = self.fs.open_upload_stream(
            obj_name, chunk_size_bytes=CHUNK_SIZE,
            metadata=metadata)
        # with open(filepath, mode='rb') as dst:
        # Перемотаем буфер к началу
        filepath.seek(0)
        # запись данных
        grid_in.write(filepath)  # grid_in.write(file_like_obj)
        # закрываем instance при этом инициируется отправка  еще не отправленных данных
        grid_in.close()  # uploaded on close
        # обнулим буфер не удаляя объекта
        filepath.truncate(0)
        return grid_in._id

    def download(self, obj_name, filepath, version=-1):
        """

        :param obj_name: string
            название объекта value поля filename
        :param filepath: file_object
            куда будет загружены данные
        :param version:
            номер версии
            Revision numbers are defined as follows:
            0 = the original stored file
            1 = the first revision
            2 = the second revision
            etc…
            -2 = the second most recent revision
            -1 = the most recent revision
        :return: None
        """
        # with open(filepath, mode='wb') as dst:
        filepath.seek(0)
        # download_to_stream_by_name ничего не возвращает
        self.fs.download_to_stream_by_name(obj_name, filepath, revision=version)
        filepath.seek(0)

    def delete(self, keyname):
        """Удалиение документа по filename
        :param keyname: string
            filename
        :param return:
        """
        # получаем итератор ответа на запрос
        cur = self.fs.find({"filename": keyname})
        # проходим по ответам и удаляем соответствующие документы
        for item in cur:
            self.fs.delete(item._id)

    def insert_one(self, data_dict):
        return self.collection.insert_one(data_dict).inserted_id

    def insert_many(self, data_dict):
        self.collection.insert_many(data_dict)

    def find(self, collection, where, select={"_id": 0}):
        return collection.find(where, select, no_cursor_timeout=True)

    # def get_projects_list(self):
    #     return self.meta.find({},
    #                           {'_id': 0, "project_name": 1}, no_cursor_timeout=True).distinct("project_name")



class H5Base:
    """
    Базовый класс скачивания, загрузки h5
    """

    def __init__(self, db, src_path=None):
        """
        Получение пути коллекции и инстанса БД
        :param db: DB_GridFS
            экземпляр класса DB_GridFS имеющий атрибут collection
        :param src_path: string
            путь к файлу проекта h5
        """
        self.db = db
        self._h5_obj = src_path
        # получаем текущую коллекцию
        self.collection = db.collection


class H5Upload(H5Base):
    """
    Класс отправки данных в БД
    """

    def __init__(self, db, src_path):
        """

        :param db: DB_GridFS
            экземпляр класса DB_GridFS имеющий атрибут collection
        :param src_path: string
            путь к файлу проекта h5
        """
        super().__init__(db, src_path)

    # @timer
    def upload(self):
        """
        Открваем h5-файл и проходим по всем его объектам
        каждый объект и его h5 путь проходит через метод self.cut
        :return: None
        """
        # with h5py.File(self.h5geo_path, mode='r') as src:
        self._h5_obj.visititems(self.cut)

    def cut(self, name, obj, ):
        """ метод для visititem вызывается для каждого объекта в hdf5 файле
        :param name: string
            имя h5 объекта вида /Геомодель/wells/Скважина-1/construction/traj_reduce_2d
        :param obj: h5 объект
            объект h5 из файла
        return:
        """

        with h5py.File(temp_path, mode='w') as dst:
            try:
                # Разделение на группы и датасеты т.к. невозможно
                # скопировать только групп без вложенных объектов
                # Если пришла группа во временном файле создаем
                # группу и переносим атрибуты
                if isinstance(obj, h5py.Group):
                    group = dst.create_group(name)
                    for key, value in obj.attrs.items():
                        # print(key, value)
                        group.attrs[key] = value
                # если датасет просто копируем во временный файл
                elif isinstance(obj, h5py.Dataset):
                    dst.copy(obj, name)

            except Exception as error:
                print(error)
                print(name, obj.name)

        # отправляем временный файл в БД
        metadata = {'version': 0}
        self.send(name, temp_path, metadata=metadata)

    def send(self, name, temp_path, metadata):
        """
        Метод  отправки в БД
        :param name: string
            имя h5 объекта вида /Геомодель/wells/Скважина-1/construction/traj_reduce_2d
        :param temp_path: file_object
            куда будет загружены данные
        :param metadata:
            дополнительные метаданные объекта
        :return:
        """
        self.db.upload(name, temp_path, metadata)


class H5Download(H5Base):
    """Класс загрузки данных из БД"""

    def __init__(self, db, dst_path):
        super().__init__(db, dst_path)

    @timer
    def download(self, version=-1):
        """
        Метод получения бинарных данных из БД и их запись в h5 файл проекта
        :param version: int
        по умолчанию загружается последняя версия
        :return: None
        """
        # для уменьшения числа открытий закрытий файла файл-приемник
        # вынесен в самое начало
        with h5py.File(self._h5_obj, mode='w') as dst:
            # получаем (find) уникальные (distinct) имена всех объектов в коллекции исключаем из ответа'_id'
            for n, item in enumerate(self.collection.find(
                    {},
                    {'_id': 0, "filename": 1}, no_cursor_timeout=True).distinct("filename")):
                # print(n, item)

                # загружаем объект по имени и версии в file object temp_path
                self.db.download(item, temp_path, version)
                # копируем объект в h5файл приемник
                # TODO переделать в функцию
                with h5py.File(temp_path, mode='r') as tmp:
                    # print(tmp[item], item)
                    # item - имя вида /Геомодель/wells/Скважина-1/construction/traj_reduce_2d
                    # tmp - корневой h5-объект во временном файле
                    # dst - корневой h5-объект в файле приемнике
                    dst.copy(tmp[item], item)
                # очищаем буфер
                temp_path.truncate(0)

    def test(self, condition):
        for n, item in enumerate(self.db.fs.find(condition).limit(5)):
            print(n, item.filename)


class Example:
    def __init__(self):
        db = MongoClient().GEOSIM_PRIOBKA
        self.collection = db.fs.files

    def query(self, query=None):
        # self.collection.insert_one({'q':'1'}).inserted_id
        return self.collection.find({}, {'_id': 0, "filename": 1})


class Select(H5Base):
    def __init__(self, db):
        super().__init__(db)

    def get_db_state(self):
        return self.collection.find({}, {'_id': 0, "filename": 1, 'md5': 1}, no_cursor_timeout=True)


class DBMongoPush(DB_GridFS):
    def __init__(self, config_params, database, collection_name):
        super().__init__(config_params, database)
        self.collection = self.db[collection_name]

    def serialize(self, filename, h5_obj):
        h5_simple_copy(temp_path, h5_obj, filename)

    def push(self, filename, h5_root, version, action):
        """
        Метод для операции push
        :param filename: Имя измененого удаленного или добавленного объекта h5
        :param h5_root: корневой элемент h5 открытого проекта
        :param version: версия проекта
        :param action: действие del или add
        :return:
        """
        self.serialize(filename, h5_root[filename])
        id = self.upload(filename, temp_path, metadata={'version': version})  # file object имеющий метод read
        # id = '5cf0d9669de53356a8a072fd'
        # сохраняем данные для синхронизаци
        self.save_ver_meta(filename=filename, version=version, action=action, id=id)

    def save_ver_meta(self, **kargs):
        print(self.insert_one(kargs))


if __name__ == '__main__':
    import pstats
    import cProfile
    from multiprocessing import Process
    import sys
    from plugins.geosim.database.sync.sqllocal import DB_sql

    # def upl(db, f):
    #     uploader = H5Upload(db, f)
    #     uploader.upload()

    path = r'D:\GEOSIM PROJECTS\db_del.h5geo'
    path = r'D:\GEOSIM PROJECTS\filters2.h5geo'
    path = r'D:\GEOSIM PROJECTS\big_test.h5geo'
    # path = r'D:\obmen\geosim\Урок7_Моделирование свойств11.h5geo'
    # path = r'D:\GEOSIM PROJECTS\normalize_new.h5geo (3).h5geo'
    # path2 = r'D:\GEOSIM PROJECTS\123.txt'
    # path = r'D:\GEOSIM PROJECTS\COORD.h5geo'
    # path = r'D:\obmen\geosim\geodata\priobka_geo.h5geo'

    # upload(path)
    # download(path, 'filters2.h5geo')
    # get_by_hash()
    # name_key = 'COORD_big'

    db = DB_GridFS(config_params, database)
    db_lite = DBMongoBase(config_params)
    git = DBMongoPush(config_params, database, 'versioning')
    ## with h5py.File(path, mode='r') as h5_root:
    ##         uploader = H5Upload(db, h5_root)
    ##         cProfile.run("uploader.upload()", 'stat')
    ##
    ## p = pstats.Stats('stat')
    ## p.strip_dirs().sort_stats('tottime').print_stats()

    # proc = Process(target=upl, args=(db, h5_root))
    # # procs.append(proc)
    # proc.start()

    # downloader = H5Download(db, 'result.h5geo')
    # cProfile.run("hashlib.md5(b'abcdefghijkl').digest()")
    # downloader.download()

    # fd = open(path, mode='rb')
    # db.delete('COORD')
    # db.upload(name, path)
    # db.download(name, path2)
    # db.delete(name)

    # db.download_uncompress(name, path2)
    import sys

    ######################################################
    dbs = Select(db)
    # # l = {i["filename"]: i["md5"] for i in dbs.get_db_state()}
    # dbsql = DB_sql()
    # for i in dbs.get_db_state():
    #     dbsql.insert(i["filename"], i["md5"])
    # # print(sys.getsizeof(l))
    # dbsql.close()
    #############################################################
    # print(type(db.get_projects_list()))
    # print(db_lite.get_projects_list())
    obj_name = 'test'
    h5_obj = 'h5file'
    version = 2
    # for i in range(500):
    #     git.push(obj_name, h5_obj, version)
    # print(list(git.find(git.collection, {"_id": ObjectId("5cf0d9669de53356a8a072fd")}, {'filename': 1, '_id': 0})))
    # git.push()
    print(list)
