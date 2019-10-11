"""
Програма для пошуку фото в директорії,
записування данних в локальну базу даних
та подальшої відправки на інший сервер

"""

import os
import sqlite3
from glob import glob
import base64
import json
import requests


DATA_BASE = 'NAME DATABASE'
DIRECT = glob('PATH*')

URL = 'URL'
TOKEN = "TOKEN"
HOST = 'HOST'


def date_convert(srn):
    """
    функція для дати

    :param srn:
    :return: Date in format dd.mm.yyyy HH:MM:SS:MS
    """
    year = srn[:4]
    month = srn[4:6]
    day = srn[6:8]
    hour = srn[8:10]
    minute = srn[10:12]
    sec = srn[12:14]
    m_sec = srn[14:]
    return f'{year}-{month}-{day}T{hour}:{minute}:{sec}.{m_sec}+02:00'


def spl_date(filename):
    """
    функція роботи з назвою файлу

    :param filename:
    :return: date, num
    """
    name = filename.split('_')  # розділяє назву на чистини по _
    f_date = name[0]  # присвоюєм дату
    num = name[1]  # присвоюєм номер
    date = date_convert(f_date)
    return date, num


def folderparse(wlk):
    """
    ф-ція перебору файлів у папці

    :param wlk:
    :return: None
    """
    date, fom = os.path.splitext(wlk)  # відділяєм формат від назви файлу
    if fom == '.jpg':  # перевірям чи формат відповідає
        vehicle = spl_date(date)  # магія
        print(vehicle)
        insert(vehicle, wlk)
        file = import_pict_binary(wlk)
        file_encode = base64.b64encode(file).decode('utf-8')
        import_json(vehicle, file_encode)
        # shutil.copy2(wlk, 'D:\\arhiv')
    else:  # якщо ні виводим помилку
        print('This is don\'t .jpg')


def insert(date, pict_path):
    """
    запис в базу даних

    :param pict_path:
    :type date: tuple
    """
    binary_pict = import_pict_binary(pict_path)
    query = (pict_path, binary_pict)
    date += query
    try:  # обробка виключень
        CURSOR.execute("INSERT INTO tz (ddk, num_tz, path, img) VALUES (?, ?, ?, ?)", date)
        print('Recorded')
        CONNECT.commit()
    except sqlite3.DatabaseError as error:  # видає помилку якщо вона є
        print('Error: ' + str(error))


def import_pict_binary(pict_path):
    """
    конвертуєм файл в бінарний для запису в БД

    :param pict_path: файл
    :return: pict_path
    """
    file = open(pict_path, 'rb')
    pict_binary = file.read()
    return pict_binary


def import_json(file, enc):
    """
    створюєм json і відправляєм на сервак

    :param file: tuple
    :param enc: encoding file in utf-8
    :return: None
    """
    data = {
        'version': 1,
        "provider": "police26",
        'data': {
            'device': {
                'id': '24484',
                'name': f'{name}'
            },
            'event': {
                'id': 'f5fc9132-067a-46c1-b62c-d194d59f1a60',
                'datetime': f'{file[0]}',
                'latitude': 48.9140583,
                "longitude": 24.7475009,
                "params": [
                    {
                        "key": "direction",
                        "value": "1"
                    },
                    {"key": "probability",
                     "value": "90"
                     }
                ],
                "vehicle": {
                    "licensePlate": {
                        "value": f"{file[1]}",
                        "country": None,
                        "region": None
                    }, "params": [
                    {
                        "key": None,
                        "value": None
                    }]
                },
                "media": [
                    {
                        "id": "f5fc9132-067a-46c1-b62c-d194d59f1a60",
                        "data": f"{enc}",
                        "url": None,
                        "plate": {
                            "data": None,
                            "url": None
                        }
                    }
                ]
            }
        }
    }
    # data_string = json.dumps(data)
    # with open('data.json', 'w') as f:
    #   f.write(json.dumps(data))
    #   f.close()
    # print(json.loads(data_string))
    headers = {'Host': f'{URL}', 'Content-type': 'application/json', 'Authorization': f'{TOKEN}'}
    request = requests.post(URL, data=json.dumps(data), headers=headers)
    print(request.status_code, request.reason)


# перевіряє на існування бази даних
if not os.path.exists(DATA_BASE):
    try:
        # створення бази + створення таблиці
        print('The database is missing \nCreated DataBase!')
        CONNECT = sqlite3.connect(DATA_BASE)
        # якщо нема бази створеної то вона автоматично ствоюється
        CURSOR = CONNECT.cursor()
        CURSOR.execute('''CREATE TABLE tz (ddk data , num_tz text, path text, img blob)''')
        CONNECT.commit()
        print('DataBase create')
    except sqlite3.DatabaseError as error:
        print('Error: ' + str(error))
else:  # якщо база вже є то просто підключаємся до неї
    print('DataBase in ' + str(os.getcwd() + '\\' + str(DATA_BASE)))
    CONNECT = sqlite3.connect(DATA_BASE)
    CURSOR = CONNECT.cursor()

for d in DIRECT:
    os.chdir(str(d))
    print(d)
    for i in os.listdir(d):
        folderparse(i)
CURSOR.close()
CONNECT.close()
