import time
from datetime import datetime
from random import randint
import logging


import pandas as pd
import xlwings
import xlwings as xw
import numpy as np

import pyodbc


def search(cursor):

    bucs_W = {}
    bucs_WL = {}
    bucs_WP = {}
    rings = {}

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

    return bucs_W, bucs_WL, bucs_WP, rings


def parametr_lab(wbxl):
    r = 2

    lab_in_object = {}

    while wbxl.sheets['Object'].range('A' + str(r)).value != None:

        SKV = wbxl.sheets['Object'].range('B' + str(r)).value
        GLUB = float(str(wbxl.sheets['Object'].range('C' + str(r)).value).replace(',','.'))
        LAB_NO = wbxl.sheets['Object'].range('A' + str(r)).value

        W = wbxl.sheets['Object'].range('T' + str(r)).value
        Ro = wbxl.sheets['Object'].range('V' + str(r)).value
        Wl = wbxl.sheets['Object'].range('AB' + str(r)).value
        Wp = wbxl.sheets['Object'].range('AC' + str(r)).value

        Ves = 100
        А10 = wbxl.sheets['Object'].range('E' + str(r)).value
        A5 = wbxl.sheets['Object'].range('F' + str(r)).value
        A2 = wbxl.sheets['Object'].range('G' + str(r)).value
        A1 = wbxl.sheets['Object'].range('H' + str(r)).value
        A05 = wbxl.sheets['Object'].range('I' + str(r)).value
        A025 = wbxl.sheets['Object'].range('J' + str(r)).value
        A01 = wbxl.sheets['Object'].range('K' + str(r)).value
        A005 = wbxl.sheets['Object'].range('L' + str(r)).value

        Ip = wbxl.sheets['Object'].range('AD' + str(r)).value
        Grunt = wbxl.sheets['Object'].range('AU' + str(r)).value

        lab_in_object.setdefault(LAB_NO, [SKV, GLUB, LAB_NO, W, Ro, Wl, Wp, Ves, А10, A5, A2, A1, A05, A025, A01, A005, Ip, Grunt])

        r = str(int(r) + 1)

    return lab_in_object

def new_dict(lab_in_object, bucs_W, bucs_WL, bucs_WP, rings):
    new_dict = {}
    for LAB_NO in lab_in_object.keys():
        list_parametr = lab_in_object.get(LAB_NO)

        try:
            Ip = float(str(list_parametr[16]).replace(',','.'))
        except:
            Ip = None

        skv = list_parametr[0]
        depth_ot = list_parametr[1]
        lab_num = list_parametr[2]

        # роспись влажности
        W_value = list_parametr[3]
        K_W = (randint(10, 50)) / 100
        if Ip == None:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W1 = float(str(W_value).replace(',','.'))
            m1 = float((randint(5000, 8000)) / 100)
            m0 = round(float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)), 2)

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w0, wet_w0, dry_w0 = NUM, m1, m0
            bucs_w1, wet_w1, dry_w1 = '', '', ''
        else:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W1 = float(str(W_value).replace(',','.')) + K_W
            m1 = float((randint(5000, 8000)) / 100)
            m0 = round(float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)), 2)

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w0, wet_w0, dry_w0 = NUM, m1, m0

            # 2 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W2 = float(str(W_value).replace(',','.')) - K_W
            m1 = float((randint(5000, 8000)) / 100)
            m0 = round(float((W2 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100)), 2)

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w1, wet_w1, dry_w1 = NUM, m1, m0

        # роспись плотности
        Ro_value = list_parametr[4]
        if Ip != None and Ro_value != None:
            RING_OBJID = random_BUC(rings)
            VES_0 = float(rings.get(RING_OBJID)[0])
            OBJEM_0 = float(rings.get(RING_OBJID)[1])

            VES1R = round(float(str(Ro_value).replace(',','.')) * OBJEM_0 + VES_0, 2)

            NUM = str(rings.get(RING_OBJID)[2])

            ring_num, soil_weight = NUM, VES1R
        else:
            ring_num, soil_weight = '', ''

        # роспись текучки
        WL_value = list_parametr[5]
        if Ip != None:
            K_W = (randint(10, 50)) / 100

            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_WL)
            W1 = float(str(WL_value).replace(',','.')) + K_W
            m1 = float((randint(3500, 5000)) / 100)
            m0 = round(float((W1 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)), 2)

            NUM = str(bucs_WL.get(BUCS_OBJID)[1])

            bucs_wl0, wet_wl0, dry_wl0 = NUM, m1, m0

            # 2 бюкс
            BUCS_OBJID = random_BUC(bucs_WL)
            W2 = float(str(WL_value).replace(',','.')) - K_W
            m1 = float((randint(3500, 5000)) / 100)
            m0 = round(float((W2 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100)), 2)

            NUM = str(bucs_WL.get(BUCS_OBJID)[1])

            bucs_wl1, wet_wl1, dry_wl1 = NUM, m1, m0

        else:
            bucs_wl0, wet_wl0, dry_wl0 = '', '', ''
            bucs_wl1, wet_wl1, dry_wl1 = '', '', ''

        # роспись раската
        WP_value = list_parametr[6]
        if Ip != None:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_WP)
            W1 = float(str(WP_value).replace(',','.'))
            m1 = float((randint(1500, 1800)) / 100)
            m0 = round(float((W1 * bucs_WP.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)), 2)

            NUM = str(bucs_WP.get(BUCS_OBJID)[1])

            bucs_wp0, wet_wp0, dry_wp0 = NUM, m1, m0

        else:
            bucs_wp0, wet_wp0, dry_wp0 = '', '', ''


        # роспись ГС

        if  list_parametr[14] != None:
            try:
                vesgss = float(str(list_parametr[7]).replace(',','.'))
            except:
                vesgss = ''
            try:
                a10 = float(str(list_parametr[8]).replace(',','.'))
            except:
                a10 = ''
            try:
                a5 = float(str(list_parametr[9]).replace(',','.'))
            except:
                a5 = ''
            try:
                a2 = float(str(list_parametr[10]).replace(',','.'))
            except:
                a2 = ''
            try:
                a1 = float(str(list_parametr[11]).replace(',','.'))
            except:
                a1 = ''
            try:
                a05 = float(str(list_parametr[12]).replace(',','.'))
            except:
                a05 = ''
            try:
                a025 = float(str(list_parametr[13]).replace(',','.'))
            except:
                a025 = ''
            try:
                a01 = float(str(list_parametr[14]).replace(',','.'))
            except:
                a01 = ''

        else:
            vesgss, a10, a5, a2, a1, a05, a025, a01 = '', '', '', '', \
                '', '', '', ''

        # Grunt
        Grunt = list_parametr[17].split(' ')
        if list_parametr[14] != None:
            Main_type = Grunt[0] # пески
            Type_disp = Grunt[1]
        else:
            try:
                Main_type = f"{Grunt[0]} {Grunt[1]}" # глинистые
                Type_disp = Grunt[2]
            except:
                Main_type = f"{Grunt[0]}"  # глинистые
                Type_disp = Grunt[1]

        new_dict[LAB_NO] = [skv, depth_ot, lab_num,
         bucs_w0, wet_w0, dry_w0,
         bucs_w1, wet_w1, dry_w1,
         ring_num, soil_weight,
         bucs_wl0, wet_wl0, dry_wl0,
         bucs_wl1, wet_wl1, dry_wl1,
         bucs_wp0, wet_wp0, dry_wp0,
         vesgss, a10, a5, a2, a1, a05, a025, a01, Main_type, Type_disp]

    return new_dict


def random_BUC(dict_bucs):
    len_dict = len(dict_bucs)

    choise_random = randint(0, len_dict - 1)

    count = 0
    for buc in dict_bucs.keys():
        BUCS_OBJID = buc
        if choise_random == count:
            return BUCS_OBJID
        else:
            count += 1


# main part
# main part
# main part

try:
    start_time = datetime.now()  # замер времени


    # my_file = open("Z:\Zapis\Object\Base_for_rewrite.txt")
    name_base = 'C:/Users/MSI GP66/Desktop/HETA_base/HETA.mdb' # my_file.read()
    # my_file.close()
    # print(name_base)

    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))


    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + (name_base) + '')
    cursor = conn.cursor()

    wbxl = xw.Book('Z:/Object.xlsx')

    object = input('Введите краткое название объекта:  ')

    # получение словаря по бюксам, кольцам
    bucs_W, bucs_WL, bucs_WP, rings = search(cursor)

    # создание параметров лабораторки
    lab_in_object = parametr_lab(wbxl)

    new_dict = new_dict(lab_in_object, bucs_W, bucs_WL, bucs_WP, rings)

    print(type(new_dict))

    print(new_dict.get('1 '))




    df = pd.DataFrame(new_dict)
    df = df.transpose()

    df = df.rename(columns={
        0: "n_skv", 1: "depth_from", 2: "lab_num",
        3: "bucs_w0", 4: "wet_w0", 5: "dry_w0",
        6: "bucs_w1", 7: "wet_w1", 8: "dry_w1",
        9: 'ring_num', 10: "ro_weight",
        11: "bucs_wl0", 12: "wet_wl0", 13: "dry_wl0",
        14: "bucs_wl1", 15: "wet_wl1", 16: "dry_wl1",
        17: "bucs_wp0", 18: "wet_wp0", 19: "dry_wp0",
        20: "gss_weight", 21: "a10", 22: "a5", 23: "a2",
        24: "a1", 25: "a05", 26: "a025", 27: "a01"
    })
    space_list = [
        [3, 'space_date', ''],
        [4, 'space_w0', ''],
        [8, 'space_w1', ''],
        [12, 'space_ro0', ''],
        [14, 'space_ro1', ''],
        [16, 'space_wl0', ''],
        [20, 'space_wl1', ''],
        [24, 'space_wp0', ''],
        [28, 'space_gss', ''],
        [37, 'space_gss_1', '']]


    for i in space_list:
        df.insert(i[0], i[1], i[2])

    har_list = ["depth_from", "wet_w0", "dry_w0", "wet_w1", "dry_w1",
                "ro_weight", "wet_wl0", "dry_wl0", "wet_wl1", "dry_wl1",
                "wet_wp0", "dry_wp0", "gss_weight", "a10", "a5", "a2", "a1",
                "a05", "a025", "a01"]

    df[har_list] = df[har_list].astype("float64", errors='ignore')
    df[har_list] = df[har_list].round(2)
    df[har_list] = df[har_list].astype("str")
    df[har_list] = df[har_list].stack().str.replace('.', ',', regex=True).unstack()
    df.fillna('')
    sorted_df = df.sort_values(by='lab_num')
    sorted_df = sorted_df.transpose()



    print(sorted_df)
    print(sorted_df.info())
    sorted_df.to_csv(f"Z:/{object}.log", sep='\t', index=False, header=False)


except Exception as err:
    print('Исправляй  ' + lab_in_object.get(lab))

    logging.exception(err)

    Di = input()

print(datetime.now() - start_time)
Di = input()
