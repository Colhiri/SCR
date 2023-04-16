import logging
import math
import os
import random
import shutil
import time
from datetime import datetime
from random import randint
import sys
sys.setrecursionlimit(30000)


import numpy
import numpy as np
import pandas as pd
import pyodbc

import connect_class_b as cc



def search(cursor, object_name):

    lab_in_object = {}
    skv_in_object = {}


    water_in_object = {}



    try:
        select = "SELECT OBJID FROM WOBJECT WHERE NAMEOBJ_SHORT = ?"
        OBJID_OBJECT = list(cursor.execute(select, object_name).fetchall()[0])[0]
    except:
        print('Такого объекта не существует!')
        OBJID_OBJECT = None

    # скважины в объекте
    select = "SELECT OBJID, N_SKV FROM SK WHERE AWORK_OBJID = ?"
    OBJID_SKV = (cursor.execute(select, OBJID_OBJECT).fetchall())

    for x in range(len(OBJID_SKV)):
        skv_in_object.setdefault(OBJID_SKV[x][0], OBJID_SKV[x][1])

    # лабораторки в объекте
    for skv in skv_in_object.keys():
        select = "SELECT OBJID, LAB_NO, GLUB_OT, GLUB_DO, GRNT_CLASS FROM PROBAGR WHERE COD = ?"
        OBJID_LAB = list(cursor.execute(select, skv).fetchall())
        for x in range(len(OBJID_LAB)):
           lab_in_object.setdefault(OBJID_LAB[x][0], [skv_in_object[skv], OBJID_LAB[x][2], OBJID_LAB[x][3], OBJID_LAB[x][1], OBJID_LAB[x][4]])



    # ВОДИЧКА
    for skv in skv_in_object:
        select = "SELECT OBJID, LAB_NO, GLUB FROM VDOPR WHERE COD = ?"
        OBJID_LAB = list(cursor.execute(select, skv).fetchall())
        for x in range(len(OBJID_LAB)):
            try:
                water_in_object.setdefault(OBJID_LAB[x][0], [skv_in_object[skv], round(OBJID_LAB[x][2], 1), OBJID_LAB[x][1]])
            except:
                continue

    SKV = None
    GLUB_OT = None
    GLUB_DO = None
    LAB_NO = None
    W = None
    Ro = None
    Wl = None
    Wp = None
    TPS = None
    TPD = None
    SPS = None
    SPD = None
    Gransost = None
    FI = None
    kF = None
    Organic = None
    SKAL_GRNT = None
    CHEMESTRY_WATER = None
    CHEMESTRY_GRNT = None
    DOP = None
    RZG = None

    lab_parametr = {}
    # создание словаря по лабораторкам с параметрами
    for num, lab in enumerate(lab_in_object.keys(), 1):
        """
        # Скальный грунт или нет известно из PROBAGR (уже включено в список лаб номеров)
        
        # Влажность, плотность, текучка, раскат, угол естественного откоса, органика берется из SVODKA_FIZMEX
        
        # Грансостав из SVODKA_GRANS
        
        # Коэф.фильтрации из SVODKA_FILTR
        
        Доп.нагрузка только через CM3EXAM или SDDATA
        
        # Прочность, деформация. деформация с разгрузкой из SVODKA_CM3
        
        # Обычная компрессия из SVODKA_CM
        
        # Обычный срез из SVODKA_SD
        
        # Химия грунта берется из SVODKA_ZASOL
        
        # Химия воды из VDOPR
        """
        SKV = None
        GLUB_OT = None
        GLUB_DO = None
        LAB_NO = None
        W = None
        Ro = None
        Wl = None
        Wp = None
        TPS = None
        TPD = None
        SPS = None
        SPD = None
        Gransost = None
        FI = None
        kF = None
        Organic = None
        SKAL_GRNT = None
        CHEMESTRY_WATER = None
        CHEMESTRY_GRNT = None
        DOP = None
        RZG = None

        SKV = lab_in_object[lab][0]
        GLUB_OT = round(lab_in_object[lab][1], 1)
        GLUB_DO = round(lab_in_object[lab][2], 1)
        LAB_NO = lab_in_object[lab][3]
        SKAL_GRNT = '+' if lab_in_object[lab][4] == 1 else None
        if SKAL_GRNT:
            lab_parametr.setdefault(lab, [num, SKV, f"{GLUB_OT}-{GLUB_DO}", LAB_NO, W, Ro, Wl, Wp, TPS, TPD, SPS, SPD,
                                          Gransost, FI, kF, Organic, SKAL_GRNT, CHEMESTRY_WATER, CHEMESTRY_GRNT, DOP, RZG])
            continue

        print(LAB_NO)


        select = "SELECT OBJID, PROBAGR_OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
        PROBEGR_SVODKA = list(cursor.execute(select, lab).fetchall()[0])[0]
        PROBAGR_OBJID = list(cursor.execute(select, lab).fetchall()[0])[1]



        select = "SELECT OBJID, PH, Ca, Mg FROM SVODKA_ZASOL WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        PH = None if result[0][1] is None else '+'
        Ca = None if result[0][2] is None else '+'
        Mg = None if result[0][3] is None else '+'
        CHEMESTRY_GRNT = '+' if PH or Ca or Mg else None
        if CHEMESTRY_GRNT:
            lab_parametr.setdefault(lab, [num, SKV, f"{GLUB_OT}-{GLUB_DO}", LAB_NO, W, Ro, Wl, Wp, TPS, TPD, SPS, SPD,
                                          Gransost, FI, kF, Organic, SKAL_GRNT, CHEMESTRY_WATER, CHEMESTRY_GRNT, DOP, RZG])
            continue



        select = "SELECT OBJID, W, Wl, Wp, Ro, FIs, FIw, Organic FROM SVODKA_FIZMEX WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())

        try:
            W = None if result[0][1] is None else '+'
        except:
            continue
        Wl = None if result[0][2] is None else '+'
        Wp = None if result[0][3] is None else '+'
        Ro = None if result[0][4] is None else '+'
        FIs = None if result[0][5] is None else '+'
        FIw = None if result[0][6] is None else '+'
        Organic = None if result[0][7] is None else '+'

        LAB_FOR_PR = str(LAB_NO).split('-')[0]

        select = "SELECT OBJID, G01_005 FROM SVODKA_GRANS WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        try:
            Gransost = None if result[0][0] is None else '+'
        except:
            pass
        # Gransost = None if result[0][1] is None else '+'

        select = "SELECT OBJID FROM SVODKA_FILTR WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        try:
            kF = None if result[0][0] is None else '+'
        except:
            pass


        # механика
        select = "SELECT OBJID, CM3_KD_F, CM3_KD_E, CM3_KD_E2 FROM SVODKA_CM3 WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        try:
            TPS = None if result[0][1] is None else '+'
        except:
            pass
        try:
            TPD = None if result[0][2] is None else '+'
        except:
            pass
        try:
            RZG = None if result[0][3] is None else '+'
        except:
            pass



        select = "SELECT OBJID FROM SVODKA_SD WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        try:
            SPS = None if result[0][0] is None else '+'
        except:
            pass



        select = "SELECT OBJID FROM SVODKA_CM WHERE OBJID = ?"
        result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
        try:
            SPD = None if result[0][0] is None else '+'
        except:
            pass


        if TPS:
            # дополнительные давления на трехосниках
            select = "SELECT OBJID FROM CM3OPR WHERE PROBEGR_ID = ?"
            result = list(cursor.execute(select, PROBAGR_OBJID).fetchall())

            CM3_OBJID = None if result[0][0] is None else result[0][0]


            if CM3_OBJID:
                DOP = '+'
                select = "SELECT OBJID, UNIFORM_PRESSURE, EXAM_NUM FROM CM3EXAM WHERE OBJID = ? and FROM_MORECULON = -1"
                result = list(cursor.execute(select, CM3_OBJID).fetchall())
                press_1 = round(float(result[0][1]), 3)
                EXAM_NUM = result[0][2]
                if press_1 in [0.1, 0.15, 0.2, 0.3, 0.5]:
                    # select = f"SELECT OBJID, UNIFORM_PRESSURE FROM CM3EXAM WHERE OBJID = ? and FROM_MORECULON = -1 and EXAM_NUM = ?"
                    # result = list(cursor.execute(select, CM3_OBJID, EXAM_NUM + 1).fetchall())
                    # press_2 = round(float(result[0][1]), 3)
                    # if press_2 in [0.1, 0.15, 0.2, 0.3, 0.5]:
                    #     select = f"SELECT OBJID, UNIFORM_PRESSURE FROM CM3EXAM WHERE OBJID = ? and FROM_MORECULON = -1 and EXAM_NUM = {str(EXAM_NUM + 2)}"
                    #     result = list(cursor.execute(select, CM3_OBJID).fetchall())
                    #     press_3 = round(float(result[0][1]), 3)
                    #     if press_3 in [0.1, 0.15, 0.2, 0.3, 0.5]:
                    DOP = None
            if DOP:
                DOP = int((4000 * press_1 - 20 * GLUB_OT) / 10) * 10 # int((GLUB_OT * 20 - press_1) * 1000)

        if SPS:
            # дополнительные давления на срезах
            select = "SELECT OBJID FROM SDOPR WHERE PROBAGR_OBJID = ?"
            result = list(cursor.execute(select, PROBAGR_OBJID).fetchall())
            try:
                SD_OBJID = None if result[0][0] is None else result[0][0]
            except:
                SD_OBJID = None


            if SD_OBJID:
                select = "SELECT OBJID, P FROM SDDATA WHERE OBJID = ?"
                result = list(cursor.execute(select, SD_OBJID).fetchall())
                press_1 = round(float(result[0][1]), 3)
                if press_1 in [0.1, 0.15, 0.2, 0.3, 0.5]:
                    DOP = None
                else:
                    DOP = int((4000 * press_1 - 20 * GLUB_OT) / 10) * 10

        lab_parametr.setdefault(lab, [num, SKV, f"{GLUB_OT}-{GLUB_DO}", LAB_NO, W, Ro, Wl, Wp, TPS, TPD, SPS, SPD,
                                      Gransost, FI, kF, Organic, SKAL_GRNT, CHEMESTRY_WATER, CHEMESTRY_GRNT, DOP, RZG])

    SKV = None
    GLUB_OT = None
    GLUB_DO = None
    LAB_NO = None
    W = None
    Ro = None
    Wl = None
    Wp = None
    TPS = None
    TPD = None
    SPS = None
    SPD = None
    Gransost = None
    FI = None
    kF = None
    Organic = None
    SKAL_GRNT = None
    CHEMESTRY_WATER = None
    CHEMESTRY_GRNT = None
    DOP = None
    RZG = None

    lab_parametr.setdefault((''.join([random.choice(list('1234567890ABCDEF'))
                          for x in range(32)])), [None, None, None, None, None, None, None, None, None, None, None, None,
                                  None, None, None, None, None, None, None, None, None])


    for num, lab in enumerate(water_in_object.keys(), 1):
        lab_parametr.setdefault(lab, [num, water_in_object[lab][0], water_in_object[lab][1], water_in_object[lab][2], W, Ro, Wl, Wp, TPS, TPD, SPS, SPD,
                                      Gransost, FI, kF, Organic, SKAL_GRNT, '+', CHEMESTRY_GRNT, DOP, RZG])

    return lab_parametr, LAB_FOR_PR




try:
    start_time = datetime.now()  # замер времени

    my_file = open("Z:\Zapis\Object\Base_for_rewrite.txt")
    name_base = my_file.read()
    my_file.close()
    print(name_base)


    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))


    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + name_base + '')
    cursor = conn.cursor()



    select = "SELECT NAMEOBJ_SHORT FROM WOBJECT"
    result = list(cursor.execute(select).fetchall())


    for object_name in result:

        lab_parametr, LAB_FOR_PR = search(cursor, object_name)

        df = pd.DataFrame(lab_parametr)
        sorted_df = df.transpose()
        # writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/TPS.xlsx', mode='a', engine="openpyxl", if_sheet_exists='overlay')
#
#
        # # 1 давление
        # df_Press1.to_excel(writer, sheet_name='Лист1', startcol=11, startrow=1, index=False, index_label=False,
        #                    header=False)
        # writer.close()
#


        sorted_df.to_csv(f"D:/Резервное копирование/Ведомость назначений/{object_name}.log", sep='\t', index=False, header=False)


    print(lab_parametr)



except Exception as err:
    try:
        print('Исправляй  ' + lab_in_object.get(lab))
    except:
        pass

    logging.exception(err)

    Di = input()

print(datetime.now() - start_time)
Di = input()

