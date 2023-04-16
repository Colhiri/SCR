import logging
import random
import time
from datetime import datetime

import pandas as pd
import pyodbc

import connect_class_b as cc


# генератор id
def OBJID():
    OBJID = (''.join([random.choice(list('1234567890ABCDEF'))
                      for x in range(32)]))
    return OBJID


def search_and_create_object(cursor, name_table, parametr_d):
    try:
        select = "SELECT OBJID FROM WOBJECT WHERE NAMEOBJ_SHORT = ?"
        OBJID_OBJECT = list(cursor.execute(select, name_table).fetchall()[0])[0]
    except:
        OBJID_OBJECT = None

    if OBJID_OBJECT != None:
        parametr_write = input('Объект найден в базе, записать его в существующий объект? (y/n):  ')
        if parametr_write == 'y':
            return OBJID_OBJECT
        if parametr_write == 'n':
            OBJID_OBJECT = OBJID()
            cursor.execute(
                f"INSERT INTO WOBJECT (OBJID, NAMEOBJ_SHORT, NAMEOBJ_FULL, DATE1, DATE2, OBJTYPE_OBJID, REGION_OBJID) VALUES ('{OBJID_OBJECT}', '{name_table}', '{name_table}', '{directory_time}', '{directory_time}', 'C40C7AF7123742F585DA2A3592CEC6EE', '5965D9FA0B2042C3B9F5CEF7EF4540F4')")
            cursor.commit()
            return OBJID_OBJECT

    if OBJID_OBJECT == None:
        OBJID_OBJECT = OBJID()
        cursor.execute(
            f"INSERT INTO WOBJECT (OBJID, NAMEOBJ_SHORT, NAMEOBJ_FULL, DATE1, DATE2, OBJTYPE_OBJID, REGION_OBJID) VALUES ('{OBJID_OBJECT}', '{name_table}', '{name_table}', '{directory_time}', '{directory_time}', 'C40C7AF7123742F585DA2A3592CEC6EE', '5965D9FA0B2042C3B9F5CEF7EF4540F4')")
        cursor.commit()
        return OBJID_OBJECT


def search_and_create_skv(cursor, OBJID_OBJECT, parametr_d, parametr_proba, name_table):
    try:
        select = "SELECT OBJID,N_SKV,AWORK_OBJID FROM SK WHERE N_SKV = ? and AWORK_OBJID = ?"
        OBJID_SKV = list(cursor.execute(select, parametr_proba.get('NO_SKV'), OBJID_OBJECT).fetchall()[0])[0]
    except:
        OBJID_SKV = None

    if OBJID_SKV != None:
        return OBJID_SKV
    else:
        OBJID_SKV = OBJID()
        cursor.execute(
            f"INSERT INTO SK (OBJID, OBJECT, N_SKV, DIAM, VYRTYPE_OBJID, AWORK_OBJID, NSKV4SORT, DATASOURCE_ID, IS_STAT_SK) VALUES ('{OBJID_SKV}', '{name_table}', '{parametr_proba.get('NO_SKV')}', '0', '4F21D49AC7874F9795EDC4F52E559F55', '{OBJID_OBJECT}', '0000000009', '00000000000000000000000000000000', '0')")
        cursor.commit()

        # ПЕРЕЗАПИСЬ СКВАЖИНЫ (ПРИВЯЗКА)
        cursor.execute(f"INSERT INTO SK_PER_OBJECT (SK_OBJID, WOBJ_OBJID) VALUES ('{OBJID_SKV}','{OBJID_OBJECT}')")
        cursor.commit()

    return OBJID_SKV


def search_and_create_proba(cursor, OBJID_OBJECT, OBJID_SKV, parametr_d, parametr_proba, name_table):
    try:
        select = "SELECT OBJID,LAB_NO,COD FROM PROBAGR WHERE LAB_NO = ? and COD = ?"
        OBJID_LAB = list(cursor.execute(select, parametr_proba.get('LAB_NO'), OBJID_SKV).fetchall()[0])[0]
    except:
        OBJID_LAB = None

    if OBJID_LAB != None:
        OBJID_LAB = None
        return OBJID_LAB
    else:
        OBJID_LAB = OBJID()
        cursor.execute(
            f"INSERT INTO PROBAGR (OBJID, LAB_NO, DATA_OTBORA, GLUB_OT, GLUB_DO, COD, USE_IN_STAT, CALC_UNDER_FORMULA) VALUES ('{OBJID_LAB}','{parametr_proba.get('LAB_NO')}', '{directory_time}', '{parametr_proba.get('GLUB_OT')}', '{str(float(parametr_proba.get('GLUB_OT').replace(',', '.')) + 0.2).replace('.', ',')}', '{OBJID_SKV}', '-1', '-1')")
        cursor.commit()
        cursor.execute(f"INSERT INTO PROBAGR_OBJID (OBJID) VALUES ('{OBJID_LAB}')")
        cursor.commit()

        return OBJID_LAB


def search_BUC(cursor, parametr_d, parametr_proba, type_buc):
    select = "SELECT OBJID,P,num FROM Bucs WHERE num = ?"
    try:
        OBJID_BUC = list(cursor.execute(select, type_buc).fetchall()[0])[0]
        VES_0 = list(cursor.execute(select, type_buc).fetchall()[0])[1]
    except:
        OBJID_BUC = None
        VES_0 = None
    if OBJID_BUC != None:
        return OBJID_BUC, VES_0
    else:
        print('Бюкс не найден!  ', type_buc)
        return OBJID_BUC, VES_0


def search_RING(cursor, parametr_d, parametr_proba):
    select = "SELECT OBJID,P,V,NUM FROM Rings WHERE NUM = ?"
    try:
        RING_OBJID = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[0]
        VES0R = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[1]
        VR = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[2]
    except:
        RING_OBJID = None
        VES0R = None
        VR = None
    if RING_OBJID != None:
        return RING_OBJID, VES0R, VR
    else:
        print('Кольцо не найдено!')
        return RING_OBJID, VES0R, VR


def create_W(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
    if parametr_proba.get('BUC_W_1') != None and parametr_proba.get('VES_VLGR_W_1') != None and parametr_proba.get(
            'VES_SHGR_W_1') != None:
        OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_W_1'))
        if OBJID_BUC != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_W_1')}', '{parametr_proba.get('VES_SHGR_W_1')}')")
            cursor.commit()
    if parametr_proba.get('BUC_W_2') != None and parametr_proba.get('VES_VLGR_W_2') != None and parametr_proba.get(
            'VES_SHGR_W_2') != None:
        OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_W_2'))
        if OBJID_BUC != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_W_2')}', '{parametr_proba.get('VES_SHGR_W_2')}')")
            cursor.commit()
    return True


def create_WL(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
    if parametr_proba.get('BUC_WL_1') != None and parametr_proba.get('VES_VLGR_WL_1') != None and parametr_proba.get(
            'VES_SHGR_WL_1') != None:
        OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WL_1'))
        if OBJID_BUC != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WL_1')}', '{parametr_proba.get('VES_SHGR_WL_1')}')")
            cursor.commit()
    if parametr_proba.get('BUC_WL_2') != None and parametr_proba.get('VES_VLGR_WL_2') != None and parametr_proba.get(
            'VES_SHGR_WL_2') != None:
        OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WL_2'))
        if OBJID_BUC != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WL_2')}', '{parametr_proba.get('VES_SHGR_WL_2')}')")
            cursor.commit()
    return True


def create_WP(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
    if parametr_proba.get('BUC_WP') != None and parametr_proba.get('VES_VLGR_WP') != None and parametr_proba.get(
            'VES_SHGR_WP') != None:
        OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WP'))
        if OBJID_BUC != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_WP (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WP')}', '{parametr_proba.get('VES_SHGR_WP')}')")
            cursor.commit()
    return True


def create_RING(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
    if parametr_proba.get('RING') != None and parametr_proba.get('VES_RING') != None:
        RING_OBJID, VES0R, VR = search_RING(cursor, parametr_d, parametr_proba)
        if RING_OBJID != None:
            cursor.execute(
                f"INSERT INTO PROBAGR_PLOTNGR (OBJID, ZAMER_NO, DATA_ISP, RING_OBJID, VES0, VES1, VOL,ROP) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{RING_OBJID}', '{str(VES0R).replace('.', ',')}', '{parametr_proba.get('VES_RING')}', '{str(VR).replace('.', ',')}','0,9')")
            cursor.commit()
    return True


def GRANSOST(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
    if parametr_proba.get('VES1') != None:
        cursor.execute(
            f"INSERT INTO PROBAGR_GRANSOST (OBJID,DATA_ISP,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,VES1) VALUES ('{OBJID_LAB}','{directory_time}','{parametr_proba.get('GGR10')}','{parametr_proba.get('G10_5')}','{parametr_proba.get('G5_2')}','{parametr_proba.get('G2_1')}','{parametr_proba.get('G1_05')}','{parametr_proba.get('G05_025')}','{parametr_proba.get('G025_01')}', '{parametr_proba.get('VES1')}')")

        cursor.commit()

    return True


# main part
# main part
# main part
start_time = datetime.now()  # замер времени

name_table = input('Введите имя таблицы:   ')

NewConnect = cc.ConnectTable()
NewConnect.connect_to_googlesheet(name_table)
worksheet_journal = NewConnect.connect_to_spreadsheet('LIST')
worksheet_parametr = NewConnect.connect_to_spreadsheet('Parametr')


class PrepareData:
    pd.options.display.width = None
    pd.options.mode.chained_assignment = None

    def __init__(self, data_input):
        self.DF = None
        self.gc_object = data_input.get_values(major_dimension="rows")
        self.gc_object1 = data_input.get_values('A:B', major_dimension="rows")

    # makeFrame - создаю дф из журнала
    def makeFrame(self):
        data = {'LIMITER': [d for d in self.gc_object[0]],
                'NO_SKV': [d for d in self.gc_object[1]],
                'GLUB_OT': [d for d in self.gc_object[2]],
                'LAB_NO': [d for d in self.gc_object[3]],
                'BUC_W_1': [d for d in self.gc_object[6]],
                'VES_VLGR_W_1': [d for d in self.gc_object[7]],
                'VES_SHGR_W_1': [d for d in self.gc_object[8]],
                'BUC_W_2': [d for d in self.gc_object[10]],
                'VES_VLGR_W_2': [d for d in self.gc_object[11]],
                'VES_SHGR_W_2': [d for d in self.gc_object[12]],
                'RING': [d for d in self.gc_object[14]],
                'RING_VES': [d for d in self.gc_object[15]],
                'VES_RING': [d for d in self.gc_object[16]],
                'BUC_WL_1': [d for d in self.gc_object[18]],
                'VES_VLGR_WL_1': [d for d in self.gc_object[19]],
                'VES_SHGR_WL_1': [d for d in self.gc_object[20]],
                'BUC_WL_2': [d for d in self.gc_object[22]],
                'VES_VLGR_WL_2': [d for d in self.gc_object[23]],
                'VES_SHGR_WL_2': [d for d in self.gc_object[24]],
                'BUC_WP': [d for d in self.gc_object[26]],
                'VES_VLGR_WP': [d for d in self.gc_object[27]],
                'VES_SHGR_WP': [d for d in self.gc_object[28]],
                'VES1': [d for d in self.gc_object[30]],
                'GGR10': [d for d in self.gc_object[31]],
                'G10_5': [d for d in self.gc_object[32]],
                'G5_2': [d for d in self.gc_object[33]],
                'G2_1': [d for d in self.gc_object[34]],
                'G1_05': [d for d in self.gc_object[35]],
                'G05_025': [d for d in self.gc_object[36]],
                'G025_01': [d for d in self.gc_object[37]]
                }
        self.DF = pd.DataFrame(data)

        return self.DF

    def makeParametr(self):

        data = {}
        for x in range(len(self.gc_object1)):
            data.setdefault(self.gc_object1[x][1], self.gc_object1[x][0])

        for x in data.keys():
            update = data.get(x)
            if update == '':
                data.update({x: None})

        for x in data.keys():
            update = data.get(x)

        return data


parametr_d = PrepareData(worksheet_parametr).makeParametr()

print(parametr_d.get('path'))

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + parametr_d.get('path') + '')
cursor = conn.cursor()

directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

try:
    parametr_proba_df = PrepareData(worksheet_journal).makeFrame()

    parametr_proba = {}

    name_parametr = ['NO_SKV']

    parametr_proba.setdefault('NO_SKV', parametr_proba_df.iloc[1][1])

    if parametr_proba.get('NO_SKV') == 'None':
        parametr_proba.update({'NO_SKV': None})

    if parametr_proba.get('NO_SKV') == '':
        parametr_proba.update({'NO_SKV': None})

    OBJID_OBJECT = search_and_create_object(cursor, name_table, parametr_d)

    r = 1

    while parametr_proba.get('NO_SKV') != None:

        parametr_proba = {}

        num_row = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                   13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                   26, 27, 28, 29]
        name_parametr = ['LIMITER', 'NO_SKV', 'GLUB_OT', 'LAB_NO', 'BUC_W_1', 'VES_VLGR_W_1', 'VES_SHGR_W_1', 'BUC_W_2',
                         'VES_VLGR_W_2', 'VES_SHGR_W_2', 'RING', 'RING_VES', 'VES_RING', 'BUC_WL_1', 'VES_VLGR_WL_1',
                         'VES_SHGR_WL_1', 'BUC_WL_2', 'VES_VLGR_WL_2', 'VES_SHGR_WL_2', 'BUC_WP', 'VES_VLGR_WP',
                         'VES_SHGR_WP', 'VES1', 'GGR10', 'G10_5', 'G5_2',
                         'G2_1', 'G1_05', 'G05_025', 'G025_01']
        name_parametr_replace = ['GLUB_OT', 'VES_VLGR_W_1', 'VES_SHGR_W_1',
                                 'VES_VLGR_W_2', 'VES_SHGR_W_2', 'RING_VES', 'VES_RING', 'VES_VLGR_WL_1',
                                 'VES_SHGR_WL_1', 'VES_VLGR_WL_2', 'VES_SHGR_WL_2', 'VES_VLGR_WP',
                                 'VES_SHGR_WP', 'VES1', 'GGR10', 'G10_5', 'G5_2',
                                 'G2_1', 'G1_05', 'G05_025', 'G025_01']
        list_int_keys_parametr_proba = ['BUC_W_1', 'BUC_W_2',
                                        'RING', 'RING_VES', 'BUC_WL_1',
                                        'BUC_WL_2', 'BUC_WP']

        for num_row, name_parametr in zip(num_row, name_parametr):
            parametr_proba.setdefault(name_parametr, parametr_proba_df.iloc[r][num_row])

        for x in parametr_proba.keys():
            update = parametr_proba.get(x)
            if update == 'None':
                parametr_proba.update({x: None})

        for x in parametr_proba.keys():
            update = parametr_proba.get(x)
            if update == '':
                parametr_proba.update({x: None})

        for x in list_int_keys_parametr_proba:
            try:
                parametr_proba.update({x: int(parametr_proba.get(x))})
            except:
                pass

        for x in name_parametr_replace:
            try:
                parametr_proba.update({x: parametr_proba.get(x).replace('.', ',')})
            except:
                pass

        if parametr_proba.get('LIMITER') == 'Y':

            OBJID_SKV = search_and_create_skv(cursor, OBJID_OBJECT, parametr_d, parametr_proba, name_table)

            OBJID_LAB = search_and_create_proba(cursor, OBJID_OBJECT, OBJID_SKV, parametr_d, parametr_proba, name_table)

            if OBJID_LAB != None:
                create_W(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                create_WL(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                create_WP(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                create_RING(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                GRANSOST(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                print(parametr_proba.get('LAB_NO'))

        else:
            r += 1
            continue

        r += 1
    print(datetime.now() - start_time)
    KEK = input()

except Exception as err:
    print('Исправляй  ' + parametr_proba.get('LAB_NO'))
    logging.exception(err)
    Di = input()

# добавить в прогу дорисовку влажности если есть один бюкс, дорисовку плотности по нормативкам, расчет IL, IP и т.д.
