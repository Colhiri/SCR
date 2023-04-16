
import time
from datetime import datetime
import random
import logging
import pyodbc
from random import randint


def search(cursor, object_name):

    lab_in_object = {}

    skv_in_object = []

    bucs_W = {}
    bucs_WL = {}
    bucs_WP = {}
    rings = {}

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
        select = "SELECT OBJID, LAB_NO FROM PROBAGR WHERE COD = ?"
        OBJID_LAB = list(cursor.execute(select, skv).fetchall())
        for x in range(len(OBJID_LAB)):
           lab_in_object.setdefault(OBJID_LAB[x][0], OBJID_LAB[x][1])

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

    # создание словаря по лабораторкам с параметрами
    lab_parametr = {}
    svodka_tbl = {}
    lab_grans = {}
    for lab in lab_in_object.keys():

        try:
            select = "SELECT OBJID, PROBAGR_OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
            PROBEGR_SVODKA = list(cursor.execute(select, lab).fetchall()[0])[0]
            PROBAGR_OBJID = list(cursor.execute(select, lab).fetchall()[0])[1]

            svodka_tbl.setdefault(PROBAGR_OBJID, PROBEGR_SVODKA)

            select = "SELECT OBJID,W,Wl,Wp,Ro,Ip,RoS FROM SVODKA_FIZMEX WHERE OBJID = ?"
            result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())

            lab_parametr.setdefault(lab,
                                    [result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5],
                                     result[0][6]])

            select = "SELECT OBJID,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,G01_005 FROM SVODKA_GRANS WHERE OBJID = ?"
            result = list(cursor.execute(select, PROBEGR_SVODKA).fetchall())

            fraction = [result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7], result[0][8]]

            for x in range(8):
                if fraction[x] == None:
                    fraction[x] = 0
                else:
                    fraction[x] = str(fraction[x]).replace('.', ',')

            lab_grans.setdefault(lab, fraction)

        except:
            continue

    return lab_parametr, lab_in_object, lab_grans, svodka_tbl, bucs_W, bucs_WL, bucs_WP, rings

def random_BUC(dict_bucs):

    BUCS_OBJID = random.choice(list(dict_bucs))

    return BUCS_OBJID

def write_W(cursor, lab_parametr, lab, bucs_W):
    K_W = (randint(10, 50)) / 100

    if lab_parametr.get(lab)[5] == None:
        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        W1 = float(lab_parametr.get(lab)[1])
        m1 = float((randint(5000, 8000)) / 100)
        m0 = float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','0', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()
        return True

    if lab_parametr.get(lab)[1] != None:

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        W1 = float(lab_parametr.get(lab)[1] + K_W)
        m1 = float((randint(5000, 8000)) / 100)
        m0 = float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','0', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()

        # 2 бюкс
        BUCS_OBJID = random_BUC(bucs_W)
        W2 = float(lab_parametr.get(lab)[1] - K_W)
        m1 = float((randint(5000, 8000)) / 100)
        m0 = float((W2 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100))
        VES_0 = str(bucs_W.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','1', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()

    else:
        print('W не найдено в сводке!')
        return False

    return True

def write_WL(cursor, lab_parametr, lab, bucs_WL):

    K_W = (randint(10, 50)) / 100

    if lab_parametr.get(lab)[5] == None:
        return True

    if lab_parametr.get(lab)[2] != None:

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_WL)
        W1 = float(lab_parametr.get(lab)[2] + K_W)
        m1 = float((randint(3500, 5000)) / 100)
        m0 = float((W1 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_WL.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','0', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()

        # 2 бюкс
        BUCS_OBJID = random_BUC(bucs_WL)
        W2 = float(lab_parametr.get(lab)[2] - K_W)
        m1 = float((randint(3500, 5000)) / 100)
        m0 = float((W2 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100))
        VES_0 = str(bucs_WL.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','1', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()

    else:
        print('WL не найдено в сводке!')
        return False

    return True

def write_WP(cursor, lab_parametr, lab, bucs_WP):

    if lab_parametr.get(lab)[5] == None:
        return True

    if lab_parametr.get(lab)[3] != None:

        # 1 бюкс
        BUCS_OBJID = random_BUC(bucs_WP)
        W1 = float(lab_parametr.get(lab)[3])
        m1 = float((randint(1500, 1800)) / 100)
        m0 = float((W1 * bucs_WP.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100))
        VES_0 = str(bucs_WP.get(BUCS_OBJID)[0]).replace('.', ',')
        m0 = str(m0).replace('.', ',')
        m1 = str(m1).replace('.', ',')
        cursor.execute(
            f"INSERT INTO PROBAGR_WP (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{lab}','0', '{directory_time}', '{BUCS_OBJID}', '{VES_0}', '{m1}', '{m0}')")
        cursor.commit()

    else:
        print('WP не найдено в сводке!')
        return False

    return True

def write_RING(cursor, lab_parametr, lab, rings):

    if lab_parametr.get(lab)[5] == None:
        return True

    if lab_parametr.get(lab)[4] != None:

        # 1 бюкс
        RING_OBJID = random_BUC(rings)
        VES_0 = float(rings.get(RING_OBJID)[0])
        OBJEM_0 = float(rings.get(RING_OBJID)[1])

        VES1R = lab_parametr.get(lab)[4] * OBJEM_0 + VES_0

        VES_0 = str(VES_0).replace('.', ',')
        OBJEM_0 = str(OBJEM_0).replace('.', ',')
        VES1R = str(VES1R).replace('.', ',')

        cursor.execute(
            f"INSERT INTO PROBAGR_PLOTNGR (OBJID, ZAMER_NO, DATA_ISP, RING_OBJID, VES0, VES1, VOL,ROP) VALUES ('{lab}','0', '{directory_time}', '{RING_OBJID}', '{VES_0}', '{VES1R}', '{OBJEM_0}','0,9')")
        cursor.commit()

    else:
        print('Ro не найдено в сводке!')
        return False

    return True

def write_GRANS(cursor, lab_parametr, lab_grans, lab):

    cursor.execute(
        f"INSERT INTO PROBAGR_GRANSOST (OBJID,DATA_ISP,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,VES1) VALUES ('{lab}','{directory_time}', '{lab_grans.get(lab)[0]}', '{lab_grans.get(lab)[1]}','{lab_grans.get(lab)[2]}','{lab_grans.get(lab)[3]}','{lab_grans.get(lab)[4]}','{lab_grans.get(lab)[5]}','{lab_grans.get(lab)[6]}', '100')")
    cursor.commit()

    return True

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

    lab_parametr, lab_in_object, lab_grans, svodka_tbl, bucs_W, bucs_WL, bucs_WP, rings = search(cursor, object_name)

    for lab in lab_in_object.keys():
        try:
            if lab_parametr.get(lab)[0] != None:
                cursor.execute(f"DELETE FROM PROBAGR_W WHERE (OBJID) = '{lab}'")
                cursor.execute(f"DELETE FROM PROBAGR_WL WHERE (OBJID) = '{lab}'")
                cursor.execute(f"DELETE FROM PROBAGR_WP WHERE (OBJID) = '{lab}'")
                cursor.execute(f"DELETE FROM PROBAGR_PLOTNGR WHERE (OBJID) = '{lab}'")

                write_W(cursor, lab_parametr, lab, bucs_W)
                write_WL(cursor, lab_parametr, lab, bucs_WL)
                write_WP(cursor, lab_parametr, lab, bucs_WP)
                write_RING(cursor, lab_parametr, lab, rings)

                if lab_grans.get(lab) != None:
                    write_GRANS(cursor, lab_parametr, lab_grans, lab)
                if lab_grans.get(lab) == None:
                    cursor.execute(f"DELETE FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '{lab}'")
                    cursor.commit()

                print(lab_in_object.get(lab))
            else:
                continue
        except:
            print('Ошибка в - ', lab_in_object.get(lab))
            continue

except Exception as err:
    try:
        print('Исправляй  ' + lab_in_object.get(lab))
    except:
        pass

    logging.exception(err)

    Di = input()

print(datetime.now() - start_time)
Di = input()
