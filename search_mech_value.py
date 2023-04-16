
import time
from datetime import datetime
import random
import logging
import pyodbc
from random import randint
import pandas

def search(cursor, object_name):

    lab_in_object = {}

    skv_in_object = []


    try:
        select = "SELECT OBJID FROM WOBJECT WHERE NAMEOBJ_SHORT = ?"
        OBJID_OBJECT = list(cursor.execute(select, object_name).fetchall()[0])[0]
    except:
        print('Такого объекта не существует!')
        OBJID_OBJECT = None

    # скважины в объекте
    select = "SELECT OBJID FROM SK WHERE AWORK_OBJID = ?"
    OBJID_SKV = (cursor.execute(select, OBJID_OBJECT).fetchall())

    for x in range(len(OBJID_SKV)):
        skv_in_object.append(OBJID_SKV[x][0])

    # лабораторки в объекте
    for skv in skv_in_object:
        select = "SELECT OBJID, LAB_NO, N_IG FROM PROBAGR WHERE COD = ?"
        OBJID_LAB = list(cursor.execute(select, skv).fetchall())
        for x in range(len(OBJID_LAB)):
           lab_in_object.setdefault(OBJID_LAB[x][0], [OBJID_LAB[x][1], OBJID_LAB[x][2]])



    # создание словаря по лабораторкам с параметрами
    lab_parametr = {}
    svodka_tbl = {}
    for lab in lab_in_object.keys():

        try:
            select = "SELECT OBJID, PROBAGR_OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
            PROBEGR_SVODKA = list(cursor.execute(select, lab).fetchall()[0])[0]
            PROBAGR_OBJID = list(cursor.execute(select, lab).fetchall()[0])[1]

            svodka_tbl.setdefault(PROBAGR_OBJID, PROBEGR_SVODKA)

            # select = "SELECT OBJID,CM3_KD_F,CM3_KD_C,CM3_KD_E,CM3_KD_E2,CM3_KD_Erzg FROM SVODKA_CM3 WHERE OBJID = ?"
            # result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())
#
            # lab_parametr.setdefault(lab_in_object[lab][0,
            #                         [lab_in_object[lab][0, result[0][1], result[0][2], result[0][3], result[0][4],
            #                          result[0][5]])
#


            select = "SELECT OBJID,CM3_KD_F,CM3_KD_C,CM3_KD_E,CM3_KD_E2,CM3_KD_Erzg FROM SVODKA_CM3 WHERE OBJID = ?"
            result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())

            lab_parametr.setdefault(lab_in_object[lab][0],
                                    [lab_in_object[lab][0], result[0][1], result[0][2], result[0][3], result[0][4],
                                     result[0][5], lab_in_object[lab][1]])

           # lab_parametr.setdefault(lab_in_object[lab][0,
           #                         [lab_in_object[lab][0, round(result[0][2], 3), round(result[0][1], 2),
           #                          round(result[0][3], 2), round(result[0][5], 2), round(result[0][4], 2)])



        except:
            continue

    return lab_parametr, lab_in_object, svodka_tbl



# main part
# main part
# main part

try:
    start_time = datetime.now()  # замер времени

    my_file = open("Z:\Zapis\Object\Base_for_rewrite.txt")
    name_base = my_file.read()
    my_file.close()
    print(name_base)


    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))


    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + name_base + '')
    cursor = conn.cursor()

    object_name = input('Введите краткое название объекта:  ')

    lab_parametr, lab_in_object, svodka_tbl = search(cursor, object_name)

    df = pandas.DataFrame(lab_parametr)
    sorted_df = df.transpose()
    sorted_df.to_csv(f"Z:/Zapis/ISP/First_data_object/{object_name}.log.log", sep='\t', index=False, header=False)

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
