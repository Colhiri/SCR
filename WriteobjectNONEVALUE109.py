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
    if parametr_proba.get('VES1') != 'None':
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
                'G025_01': [d for d in self.gc_object[37]],
                'IL': [d for d in self.gc_object[67]],
                'Ip': [d for d in self.gc_object[68]]
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


def random_BUC(dict_bucs):
    BUCS_OBJID = random.choice(list(dict_bucs))

    return BUCS_OBJID

def write_W(W, bucs_W, IL):
    K_W = (randint(10, 50)) / 100

    if IL == '':
        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        NUM_BUCS = bucs_W.get(BUCS_OBJID)[1]
        W1 = float(W)
        m1 = float((randint(5000, 8000)) / 100)
        m0 = float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')

        NUM_BUCS_1, m1_1, m0_1 = None, None, None

        return NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1

    if IL != '':

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        NUM_BUCS = bucs_W.get(BUCS_OBJID)[1]
        W1 = float(W + K_W)
        m1 = float((randint(5000, 8000)) / 100)
        m0 = float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')


        # 2 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        NUM_BUCS_1 = bucs_W.get(BUCS_OBJID)[1]
        W2 = float(W - K_W)
        m1_1 = float((randint(5000, 8000)) / 100)
        m0_1 = float((W2 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1_1) / (W2 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0_1 = str(m0_1).replace('.', ',')
        m1_1 = str(m1_1).replace('.', ',')

    else:
        print('W не найдено в сводке!')
        return False

    return NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1

def write_WL(Wl, bucs_WL, IL):

    K_W = (randint(10, 50)) / 100

    if IL == None:
        return True

    if IL != None:

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_WL)
        NUM_BUCS = bucs_WL.get(BUCS_OBJID)[1]
        W1 = float(Wl + K_W)
        m1 = float((randint(3500, 5000)) / 100)
        m0 = float((W1 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_WL.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')


        # 2 бюкс
        BUCS_OBJID = random_BUC(bucs_WL)
        NUM_BUCS_1 = bucs_WL.get(BUCS_OBJID)[1]
        W2 = float(Wl - K_W)
        m1_1 = float((randint(3500, 5000)) / 100)
        m0_1 = float((W2 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1_1) / (W2 + 100))
        VES_0 = str(bucs_WL.get(BUCS_OBJID)[0]).replace('.', ',')
        m0_1 = str(m0_1).replace('.', ',')
        m1_1 = str(m1_1).replace('.', ',')


    else:
        print('WL не найдено в сводке!')
        return False

    return NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1

def write_WP(Wp, bucs_WP, IL):

    if IL == None:
        return True

    if IL != None:

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_WP)
        NUM_BUCS = bucs_WP.get(BUCS_OBJID)[1]
        W1 = float(Wp)
        m1 = float((randint(1500, 1800)) / 100)
        m0 = float((W1 * bucs_WP.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_WP.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')

    else:
        print('WP не найдено в сводке!')
        return False

    return NUM_BUCS, m1, m0

def write_RING(Ro, rings, IL):

    if IL == None:
        return True

    if IL != None:
        # name_parametr = ['LAB_NO'0, 'SKV'1, 'GLUB'2, 'N_IG'3, 'А10'4, 'А5'5, 'А2'6, 'А1'7, 'А0,5'8, 'А0,25'9, 'А0,1'10, !!!!!!!! 'rs'11, 'W'12, 'r'13,
        #                  'r,min'14, 'r,max'15, 'e'16, 'WL'17, 'Wp'18, 'Sr'19, 'Cпк'20, 'jпк'21, 'Emoed'22, 'Kф,max'23, 'Kф,min'24, 'Iom'25, 'E'26,
        #                  'j'27, 'C'28,,,,,,,,,,,,,'Ip'34, 'IL' 35, 'js' 36, 'jw' 37] + 1

        """
        Песок
        Гравелистый 2,64
        Крупный 2,65
        Средний 2,65
        Мелкий 2,66
        Пылеватый 2,66
        
        Супесь
        Супесь 2,7
        
        Суглинок
        Суглинок легкий 2,71
        Суглинок тяжелый 2,72
        
        Глина
        Глина легкая 2,73
        Глина тяжелая 2,74
        """

        # блок расчета Sr, чтобы не вылетало
        if Ip > 0 and Ip < 7:
            RoS = 2.7

        if Ip >= 7 and Ip < 12:
            RoS = 2.71

        if Ip >= 12 and Ip < 17:
            RoS = 2.72

        if Ip > 17 and Ip < 27:
            RoS = 2.73

        if Ip >= 27:
            RoS = 2.74

        pd_lab = Ro / (1 + 0.01 * W)
        koef_por = (RoS - pd_lab) / (pd_lab)
        Sr_calc = ((W * RoS) / (koef_por * 1)) / 100

        if Sr_calc > 0.99:
            k_por_calc = ((W * RoS) / (0.99)) / 100

            # плотность
            Sr_calc = ((W * RoS) / (koef_por)) / 100
            Ro = ((RoS) / (k_por_calc + 1)) * (1 + 0.01 * W)
        else:
            k_por_calc = koef_por




        # кольцо
        RING_OBJID = random_BUC(rings)
        RING = rings.get(RING_OBJID)[2]
        VES_0 = float(rings.get(RING_OBJID)[0])
        OBJEM_0 = float(rings.get(RING_OBJID)[1])

        VES1R = Ro * OBJEM_0 + VES_0

        VES_0 = str(VES_0).replace('.', ',')
        OBJEM_0 = str(OBJEM_0).replace('.', ',')
        VES1R = str(VES1R).replace('.', ',')

    else:
        print('Ro не найдено в сводке!')
        return False

    return RING, VES1R


from random import randint

def dust():
    GGR10 = 0
    G10_5 = 0
    G5_2 = 0

    min_sum = 12.5
    max_sum = 25
    G2_1 = randint(200, 500) / 100
    G1_05 = randint(300, int((min_sum - G2_1) * 100)) / 100
    G05_025 = randint(100, int((max_sum - G1_05) * 100)) / 100

    max_sum = 74 - G2_1 - G1_05 - G05_025
    min_sum = max_sum - 10
    G025_01 = randint(int(min_sum * 100), int(max_sum * 100)) / 100

    # остаток
    G01_005 = 100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025 - G025_01

    return GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005


def small():
    GGR10 = 0
    G10_5 = 0
    G5_2 = randint(10, 250) / 100

    min_sum = 12.5
    max_sum = 25
    G2_1 = randint(200, 500) / 100
    G1_05 = randint(300, int((min_sum - G2_1) * 100)) / 100

    min_sum = 12.5
    max_sum = 24
    G05_025 = randint(1250, int((max_sum - G1_05) * 100)) / 100



    max_sum = 100 - G2_1 - G1_05 - G05_025 - G5_2
    min_sum = 74 - G05_025 - G1_05 - G2_1 - G5_2
    G025_01 = randint(int(min_sum * 100), int(max_sum * 100)) / 100


    # остаток
    G01_005 = 100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025 - G025_01
    return GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005


def mid():

    min_sum = 10
    max_sum = 20
    GGR10 = randint(10, 200) / 100
    G10_5 = randint(100, 300) / 100
    G5_2 = randint(200, 500) / 100
    G2_1 = randint(500, 900) / 100

    G1_05 = randint(2000, int((50 - G2_1 - G5_2 - G10_5 - GGR10) * 100)) / 100

    min_sum = 75 - G1_05 - G2_1 - G5_2 - G10_5 - GGR10
    max_sum = 95 - G1_05 - G2_1 - G5_2 - G10_5 - GGR10
    G05_025 = randint(int(min_sum * 100), int(max_sum * 100)) / 100

    max_sum = 100 - G2_1 - G1_05 - G05_025 - G5_2 - G10_5 - GGR10
    min_sum = 74 - G2_1 - G1_05 - G05_025 - G5_2 - G10_5 - GGR10
    G025_01 = randint(int(min_sum * 100), int(max_sum * 100)) / 100

    # остаток
    G01_005 = 100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025 - G025_01
    return GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005

def large():

    min_sum = 10
    max_sum = 24
    GGR10 = randint(100, 500) / 100
    G10_5 = randint(400, 800) / 100
    G5_2 = randint(700, 1100) / 100

    G2_1 = randint(1000, 3000) / 100
    min_sum = 50 - G2_1 - G5_2 - G10_5 - GGR10
    max_sum = 75 - G2_1 - G5_2 - G10_5 - GGR10
    G1_05 = randint(int(min_sum * 100), int((50 - G2_1 - G5_2 - G10_5 - GGR10) * 100)) / 100


    G05_025 = randint(int(min_sum * 100), int(max_sum * 100)) / 100

    G025_01 = randint(10, int((100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025) * 100)) / 100

    # остаток
    G01_005 = 100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025 - G025_01
    return GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005

def gravel():
    min_sum = 25
    max_sum = 40
    GGR10 = randint(850, 1330) / 100
    G10_5 = randint(850, 1330) / 100
    G5_2 = randint(850, 1330) / 100



    G2_1 = randint(1100, 1500) / 100
    G1_05 = randint(1100, 1500) / 100
    G05_025 = randint(1100, 1500) / 100
    G025_01 = randint(1100, 1500) / 100

    # остаток
    G01_005 = 100 - GGR10 - G10_5 - G5_2 - G2_1 - G1_05 - G05_025 - G025_01
    return GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005


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


    bucs = {}
    bucs_W = {}
    bucs_WL = {}
    bucs_WP = {}
    rings = {}
    # бюксы влажности
    select = "SELECT OBJID,P,num FROM Bucs"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs.setdefault(OBJID_BUC[x][2], [OBJID_BUC[x][0], OBJID_BUC[x][1]])

    # бюксы влажности
    select = "SELECT OBJID,P,num FROM Bucs WHERE P > 20"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs_W.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])
    # бюксы текучка
    select = "SELECT OBJID,P,num FROM Bucs WHERE P > 10 and P < 20"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs_WL.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])
    # бюксы раскат
    select = "SELECT OBJID,P,num FROM Bucs WHERE P < 10"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs_WP.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])
    # кольца
    select = "SELECT OBJID,P,V,NUM FROM Rings WHERE P > 50"
    OBJID_RING = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_RING)):
        rings.setdefault(OBJID_RING[x][0], [OBJID_RING[x][1], OBJID_RING[x][2], OBJID_RING[x][3]])

    r = 1

    while parametr_proba.get('NO_SKV') != None:

        #if parametr_proba.get('LIMITER') != 'Y':
        #    break

        parametr_proba = {}

        num_row = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                   13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                   26, 27, 28, 29, 30, 31]

        name_parametr = ['LIMITER', 'NO_SKV', 'GLUB_OT', 'LAB_NO', 'BUC_W_1', 'VES_VLGR_W_1', 'VES_SHGR_W_1', 'BUC_W_2',
                         'VES_VLGR_W_2', 'VES_SHGR_W_2', 'RING', 'RING_VES', 'VES_RING', 'BUC_WL_1', 'VES_VLGR_WL_1',
                         'VES_SHGR_WL_1', 'BUC_WL_2', 'VES_VLGR_WL_2', 'VES_SHGR_WL_2', 'BUC_WP', 'VES_VLGR_WP',
                         'VES_SHGR_WP', 'VES1', 'GGR10', 'G10_5', 'G5_2',
                         'G2_1', 'G1_05', 'G05_025', 'G025_01', 'IL','Ip']
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

        if parametr_proba.get('IL') != '' and parametr_proba.get('IL') != None:
            IL = float(parametr_proba.get('IL').replace(',', '.'))
            Ip = float(parametr_proba.get('Ip').replace(',', '.'))
# 02-035-23
            Ip += random.randint(1,20) / 100

            # print(float(parametr_proba.get('VES_VLGR_W_1').replace(',', '.')))
            # print(float(parametr_proba.get('VES_SHGR_W_1').replace(',', '.')))
            # print(bucs.get(parametr_proba.get('BUC_W_1)'))[1])
            try:
                W = 100 * (float(parametr_proba.get('VES_VLGR_W_1').replace(',', '.')) - float(parametr_proba.get('VES_SHGR_W_1').replace(',', '.'))) / (float(parametr_proba.get('VES_SHGR_W_1').replace(',', '.')) - bucs.get(parametr_proba.get('BUC_W_1'))[1])




                # вычисление правильной влажности
                if Ip > 0 and Ip < 7:
                    Wp_calc = randint(601, 889) / 100

                if Ip >= 7 and Ip < 12:
                    Wp_calc = randint(800, 1065) / 100

                if Ip >= 12 and Ip < 17:
                    Wp_calc = randint(1201, 1418) / 100

                if Ip > 17 and Ip < 27:
                    Wp_calc = randint(1500, 1800) / 100

                if Ip >= 27:
                    Wp_calc = randint(1900, 2100) / 100

                Wl_calc = Wp_calc + Ip

                W_calc = (Ip * IL) + Wp_calc

                if W >= W_calc + 2 or W <= W_calc - 2:
                    W = W_calc







                Wp = W - IL * Ip

                Wl = Wp + Ip





                if Ip <= 7:
                    Ro = ((1 - IL) / (1)) * 0.11 + 2.11
                if Ip > 7 and Ip <= 17:
                    if IL <= 0:
                        Ro = ((1 - abs(IL)) / (1)) * 0.07 + 2.24
                    if IL > 0 and IL <= 0.25:
                        Ro = ((0.25 - abs(IL)) / (0.25)) * 0.03 + 2.20
                    if IL > 0.25 and IL <= 0.5:
                        Ro = ((0.5 - abs(IL)) / (0.25)) * 0.04 + 2.16
                    if IL > 0.5 and IL <= 0.75:
                        Ro = ((0.75 - abs(IL)) / (0.25)) * 0.06 + 2.1
                    if IL > 0.75 and IL <= 1:
                        Ro = ((1 - abs(IL)) / (0.25)) * 0.06 + 2.03
                if Ip > 17:
                    if IL <= 0:
                        Ro = 2.1
                    if IL > 0 and IL <= 0.25:
                        Ro = ((0.25 - abs(IL)) / (0.25)) * 0.14 + 1.93
                    if IL > 0.25 and IL <= 0.5:
                        Ro = ((0.5 - abs(IL)) / (0.25)) * 0.14 + 1.78
                    if IL > 0.5 and IL <= 0.75:
                        Ro = ((0.75 - abs(IL)) / (0.25)) * 0.13 + 1.62

                NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1 = write_W(W, bucs_W, IL)


                parametr_proba['BUC_W_1'] = NUM_BUCS
                parametr_proba['VES_VLGR_W_1'] = m1
                parametr_proba['VES_SHGR_W_1'] = m0
                parametr_proba['BUC_W_2'] = NUM_BUCS_1
                parametr_proba['VES_VLGR_W_2'] = m1_1
                parametr_proba['VES_SHGR_W_2'] = m0_1

                NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1 = write_WL(Wl, bucs_WL, IL)
                parametr_proba['BUC_WL_1'] = NUM_BUCS
                parametr_proba['VES_VLGR_WL_1'] = m1
                parametr_proba['VES_SHGR_WL_1'] = m0
                parametr_proba['BUC_WL_2'] = NUM_BUCS_1
                parametr_proba['VES_VLGR_WL_2'] = m1_1
                parametr_proba['VES_SHGR_WL_2'] = m0_1


                NUM_BUCS, m1, m0 = write_WP(Wp, bucs_WP, IL)
                parametr_proba['BUC_WP'] = NUM_BUCS
                parametr_proba['VES_VLGR_WP'] = m1
                parametr_proba['VES_SHGR_WP'] = m0

                RING, VES1R = write_RING(Ro, rings, IL)
                parametr_proba['RING'] = RING
                parametr_proba['VES_RING'] = VES1R
            except:
                pass

            # так, смотри, тебе просто нужно заменить в датафрейме нужные ячейки, они идут просто по словарю для каждой пробы

            # конечно еще грансостав нужно сделать какой нибудь, который 100 процентов бьется

            # и для песков потом одгну влажность поставить на запись, вроде как все

            # Удачи!"
        else:

                W = 100 * (float(parametr_proba.get('VES_VLGR_W_1').replace(',', '.')) - float(
                    parametr_proba.get('VES_SHGR_W_1').replace(',', '.'))) / (
                                float(parametr_proba.get('VES_SHGR_W_1').replace(',', '.')) -
                                bucs.get(parametr_proba.get('BUC_W_1'))[1])

                if W < 8:
                    W = randint(900,1200) / 100
                if W > 22:
                    W = randint(1900, 2200) / 100

                NUM_BUCS, m1, m0, NUM_BUCS_1, m1_1, m0_1 = write_W(W, bucs_W, None)

                parametr_proba['BUC_W_1'] = NUM_BUCS
                parametr_proba['VES_VLGR_W_1'] = m1
                parametr_proba['VES_SHGR_W_1'] = m0

                if parametr_proba.get('Ip') == 'dust':
                    GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005 = dust()
                if parametr_proba.get('Ip') == 'small':
                    GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005 = small()
                if parametr_proba.get('Ip') == 'mid':
                    GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005 = mid()
                if parametr_proba.get('Ip') == 'large':
                    GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005 = large()
                if parametr_proba.get('Ip') == 'gravel':
                    GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005 = gravel()


                parametr_proba['VES1'] = '100'
                parametr_proba['GGR10'] = GGR10
                parametr_proba['G10_5'] = G10_5
                parametr_proba['G5_2'] = G5_2
                parametr_proba['G2_1'] = G2_1
                parametr_proba['G1_05'] = G1_05
                parametr_proba['G05_025'] = G05_025
                parametr_proba['G025_01'] = G025_01
                # parametr_proba['G01_005'] = G01_005


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
                parametr_proba.update({x: str(parametr_proba.get(x)).replace('.', ',')})
            except:
                pass

        if parametr_proba.get('LIMITER') == 'Y':
            # if parametr_proba.get('LIMITER') != 'Y':
            #     break

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
