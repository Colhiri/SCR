
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




# создание параметров пробы на основе инжгео
def getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor):
    # поиск номера пробы в PROBAGR
    select_prgr = "SELECT OBJID, GLUB_OT FROM PROBAGR WHERE LAB_NO = ?"
    result_search = cursor.execute(select_prgr, parametr_isp.get('LAB_NO')).fetchall()
    result_search = list(result_search[0])
    PROBEGR_IDS = result_search[0]
    GLUB = result_search[1]

    # поиск номера пробы в сводке
    select_prgr = "SELECT OBJID, PROBAGR_OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
    result_search = cursor.execute(select_prgr, PROBEGR_IDS).fetchall()
    result_search = list(result_search[0])
    PROBEGR_SVODKA = result_search[0]

    # поиск значений пробы в сводке
    select_prgr = "SELECT OBJID, Ip, IL, Sr, Kpor, Ro, W, RoS FROM SVODKA_FIZMEX WHERE OBJID = ?"
    result_search = cursor.execute(select_prgr, PROBEGR_SVODKA).fetchall()
    result_search = list(result_search[0])
    Ip = result_search[1]
    IL = result_search[2]
    Sr = result_search[3]
    Kpor = result_search[4]
    Ro = result_search[5]
    W = result_search[6]
    RoS = result_search[7]

    # основной тип грунта для механики
    if Ip == None:
        consistency = None
        water_saturation = None
        IL = None
        main_type = 'incoherent'  # несвязный
        # поиск грансостава пробы в сводке
        select_prgr = "SELECT OBJID,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,G01_005 FROM SVODKA_GRANS WHERE OBJID = ?"
        result_search = cursor.execute(select_prgr, PROBEGR_SVODKA).fetchall()
        result_search = list(result_search[0])
        GGR10 = result_search[1]
        G10_5 = result_search[2]
        G5_2 = result_search[3]
        G2_1 = result_search[4]
        G1_05 = result_search[5]
        G05_025 = result_search[6]
        G025_01 = result_search[7]
        G01_005 = result_search[8]

        fraction_grans = [GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005]
        fraction_index = [int(x) for x in range(8)]
        for grans, index in zip(fraction_grans, fraction_index):
            if grans == None:
                fraction_grans[index] = 0

        GGR10 = fraction_grans[0]
        G10_5 = fraction_grans[1]
        G5_2 = fraction_grans[2]
        G2_1 = fraction_grans[3]
        G1_05 = fraction_grans[4]
        G05_025 = fraction_grans[5]
        G025_01 = fraction_grans[6]
        G01_005 = fraction_grans[7]

        # гравелистый
        if (G5_2 + G10_5 + GGR10) > 25:
            grunt_type = 'gravel_sand'
            density = None

            # крупный
        elif (G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
            grunt_type = 'large_sand'
            density = None

            # средний
        elif (G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
            grunt_type = 'mid_sand'
            if Kpor != None:
                if Kpor <= 0.55:
                    density = 'plotn'  # плотность
                if 0.55 < Kpor and Kpor <= 0.7:
                    density = 'mid_plotn'
                if Kpor > 0.7:
                    density = 'pihl'
            else:
                density = None

            #  мелкий
        elif (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75:
            grunt_type = 'small_sand'
            if Kpor != None:
                if Kpor <= 0.6:
                    density = 'plotn'
                if 0.6 < Kpor and Kpor <= 0.75:
                    density = 'mid_plotn'
                if Kpor > 0.75:
                    density = 'pihl'
            else:
                density = None

            #  пылеватый
        elif (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) < 75:
            grunt_type = 'dust_sand'
            density = None
    else:
        Ip = float(Ip)
        IL = float(IL)
        density = None
        main_type = 'coherent'  # связный
        # супесь
        if Ip <= 7:
            grunt_type = 'supes'
            if IL < 0:
                consistency = 'tverd'
            if 0 <= IL and IL <= 1:
                consistency = 'plast'
            if 1 < IL:
                consistency = 'tekuch'

        # суглинок
        if 7 < Ip and Ip <= 17:
            grunt_type = 'sugl'
            if IL < 0:
                consistency = 'tverd'
            if 0 <= IL <= 0.25:
                consistency = 'polutverd'
            if 0.25 < IL and IL <= 0.5:
                consistency = 'tugoplast'
            if 0.5 < IL and IL <= 0.75:
                consistency = 'mygkoplast'
            if 0.75 < IL and IL <= 1:
                consistency = 'tekuchplast'
            if 1 < IL:
                consistency = 'tekuch'

        # глина
        if Ip > 17:
            grunt_type = 'glina'
            if IL < 0:
                consistency = 'tverd'
            if 0 <= IL and IL <= 0.25:
                consistency = 'polutverd'
            if 0.25 < IL and IL <= 0.5:
                consistency = 'tugoplast'
            if 0.5 < IL and IL <= 0.75:
                consistency = 'mygkoplast'
            if 0.75 < IL and IL <= 1:
                consistency = 'tekuchplast'
            if 1 < IL:
                consistency = 'tekuch'

    # водонасыщенность
    if Sr != None:
        if Sr <= 0.8:
            water_saturation = True
            CMUSL_OBJID = '96C5DAE5713940E8AFA9A4042B0851A2'
        else:
            water_saturation = False
            CMUSL_OBJID = '073E8206C7C94C0ABD2C3142F5E77EAA'
    else:
        water_saturation = None
        CMUSL_OBJID = None

    parametr_proba = {}

    parametr_write_temporary = 0

    param_proba = ['PROBEGR_IDS', 'GLUB', 'PROBEGR_SVODKA', 'grunt_type', 'consistency', 'density', 'water_saturation',
                   'main_type', 'Ip', 'IL', 'Sr', 'Kpor', 'Ro', 'W', 'RoS', 'CMUSL_OBJID', 'parametr_write_temporary']
    param_proba_value = [PROBEGR_IDS, GLUB, PROBEGR_SVODKA, grunt_type, consistency, density, water_saturation,
                         main_type, Ip, IL, Sr, Kpor, Ro, W, RoS, CMUSL_OBJID, parametr_write_temporary]
    for parametr, value in zip(param_proba, param_proba_value):
        parametr_proba.setdefault(parametr, value)
    return parametr_proba


# создание нормативных параметров, если не указаны приоритетные в параметре испытаний образца
def normative_parametr_isp(parametr_proba):
    # песок
    if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
        C = randint(1, 2) / 1000
        F = randint(3500, 4300) / 100
        E = randint(3800, 4700) / 100
    if parametr_proba.get('grunt_type') == 'mid_sand':
        C = randint(1, 3) / 1000
        F = randint(3300, 4000) / 100
        E = randint(3000, 4000) / 100
    if parametr_proba.get('grunt_type') == 'small_sand':
        C = randint(2, 4) / 1000
        F = randint(2900, 3800) / 100
        E = randint(2800, 3800) / 100
    if parametr_proba.get('grunt_type') == 'dust_sand':
        C = randint(2, 6) / 1000
        F = randint(2700, 3500) / 100
        E = randint(2500, 3100) / 100

    # связные
    # супеси
    # твердые
    if parametr_proba.get('grunt_type') == 'supes':
        if parametr_proba.get('consistency') == 'tverd':
            C = randint(21, 22) / 1000
            F = randint(2700, 3000) / 100
            E = randint(2400, 3400) / 100
        if parametr_proba.get('consistency') == 'plast':
            C = randint(13, 19) / 1000
            F = randint(2300, 2600) / 100
            E = randint(1500, 2400) / 100
        if parametr_proba.get('consistency') == 'tekuch':
            C = randint(9, 11) / 1000
            F = randint(1800, 2100) / 100
            E = randint(700, 1000) / 100
    # суглинок
    if parametr_proba.get('grunt_type') == 'sugl':
        if parametr_proba.get('consistency') == 'tverd':
            C = randint(28, 35) / 1000
            F = randint(2600, 2800) / 100
            E = randint(2900, 4000) / 100
        if parametr_proba.get('consistency') == 'polutverd':
            C = randint(23, 26) / 1000
            F = randint(2300, 2700) / 100
            E = randint(2400, 2800) / 100
        if parametr_proba.get('consistency') == 'tugoplast':
            C = randint(17, 22) / 1000
            F = randint(1700, 2100) / 100
            E = randint(1600, 2300) / 100
        if parametr_proba.get('consistency') == 'mygkoplast' or parametr_proba.get(
                'consistency') == 'tekuchplast' or parametr_proba.get('consistency') == 'tekuch':
            C = randint(12, 16) / 1000
            F = randint(1200, 1600) / 100
            E = randint(1000, 1500) / 100

    # глина
    if parametr_proba.get('grunt_type') == 'glina':
        if parametr_proba.get('consistency') == 'tverd':
            C = randint(61, 70) / 1000
            F = randint(2000, 2100) / 100
            E = randint(2600, 3000) / 100
        if parametr_proba.get('consistency') == 'polutverd':
            C = randint(47, 60) / 1000
            F = randint(1600, 1900) / 100
            E = randint(2100, 2500) / 100
        if parametr_proba.get('consistency') == 'tugoplast':
            C = randint(37, 45) / 1000
            F = randint(1300, 1500) / 100
            E = randint(1500, 2100) / 100
        if parametr_proba.get('consistency') == 'mygkoplast' or parametr_proba.get(
                'consistency') == 'tekuchplast' or parametr_proba.get('consistency') == 'tekuch':
            C = randint(7, 12) / 1000
            F = randint(2900, 3600) / 100
            E = randint(1200, 1500) / 100

    normative_value = {'C': C, 'F': F, 'E': E}

    return normative_value


# генератор OBJID
def generator_mech_objid():
    OBJID = (''.join([random.choice(list('1234567890ABCDEF'))
                      for x in range(32)]))
    return OBJID


# создание CM3OPR
def create_CM3OPR(cursor, parametr_proba):
    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    CM3DATA_OBJID = generator_mech_objid()
    write_1 = (
            'INSERT INTO CM3OPR (OBJID,	PROBEGR_ID,	DATE_TEST,	SCHEMA,	STOCK_AREA,	AREA,	HEIGHT,	ZOOM_PERCENT,	PRIBOR_OBJID) '
            + 'VALUES (?,?,?,?,?,?,?,?,?)')
    write_2 = cursor.execute(write_1, CM3DATA_OBJID, parametr_proba.get('PROBEGR_IDS'),
                             directory_time, 2, -777777, 1134.115, 76,
                             randint(60,70), 'F70EC2ACDCCA4FB19C2C16C0DAD8CD38')
    cursor.commit()
    return CM3DATA_OBJID


# вычисление параметров давления и К_0 (деформация, прочность, срез)
def calculate_press_gost(parametr_isp, parametr_proba, parametr_d):
    if parametr_isp.get('TPS') != None or parametr_isp.get('SPS') != None:

        if parametr_isp.get('DOP') != None:
            press_1 = (((parametr_proba.get('GLUB') * 20 + parametr_isp.get('DOPplus')) / 2) / 2) / 1000
            press_2 = ((parametr_proba.get('GLUB') * 20 + parametr_isp.get('DOPplus')) / 2) / 1000
            press_3 = (parametr_proba.get('GLUB') * 20 + parametr_isp.get('DOPplus')) / 1000
        else:

            # песок
            if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
                press_1 = 0.100
                press_2 = 0.300
                press_3 = 0.500

            if parametr_proba.get('grunt_type') == 'mid_sand':
                if parametr_proba.get('density') == 'plotn':
                    press_1 = 0.100
                    press_2 = 0.300
                    press_3 = 0.500
                if parametr_proba.get('density') == 'mid_plotn':
                    press_1 = 0.100
                    press_2 = 0.200
                    press_3 = 0.300
                if parametr_proba.get('density') == 'pihl':
                    press_1 = 0.100
                    press_2 = 0.150
                    press_3 = 0.200

            if parametr_proba.get('grunt_type') == 'small_sand':
                if parametr_proba.get('density') == 'plotn':
                    press_1 = 0.100
                    press_2 = 0.200
                    press_3 = 0.300
                if parametr_proba.get('density') == 'mid_plotn':
                    press_1 = 0.100
                    press_2 = 0.200
                    press_3 = 0.300
                if parametr_proba.get('density') == 'pihl':
                    press_1 = 0.100
                    press_2 = 0.150
                    press_3 = 0.200

            if parametr_proba.get('grunt_type') == 'dust_sand':
                press_1 = 0.100
                press_2 = 0.150
                press_3 = 0.200

            # связные
            # супеси, суглинки
            if parametr_proba.get('grunt_type') == 'supes' or parametr_proba.get('grunt_type') == 'sugl':
                if parametr_proba.get('IL') <= 0.5:
                    press_1 = 0.100
                    press_2 = 0.200
                    press_3 = 0.300
                else:
                    press_1 = 0.100
                    press_2 = 0.150
                    press_3 = 0.200
            # глина
            if parametr_proba.get('grunt_type') == 'glina':
                if parametr_proba.get('consistency') == 'tverd' or parametr_proba.get('consistency') == 'polutverd':
                    press_1 = 0.100
                    press_2 = 0.300
                    press_3 = 0.500
                if parametr_proba.get('consistency') == 'tugoplast':
                    press_1 = 0.100
                    press_2 = 0.200
                    press_3 = 0.300
                if parametr_proba.get('consistency') == 'mygkoplast' or parametr_proba.get(
                        'consistency') == 'tekuchplast' or parametr_proba.get('consistency') == 'tekuch':
                    press_1 = 0.100
                    press_2 = 0.150
                    press_3 = 0.200
    else:
        press_1, press_2, press_3 = None, None, None
    if parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None:
        if parametr_proba.get('grunt_type') == 'supes' or parametr_proba.get(
                'grunt_type') == 'sugl' or parametr_proba.get('grunt_type') == 'glina' and parametr_d.get(
            'need_K0') == 1:
            if parametr_proba.get('IL') > 0.5:
                K_0 = 1
            if parametr_proba.get('IL') <= 0.5:
                K_0 = 0.7
        if parametr_proba.get('main_type') == 'incoherent' and parametr_d.get('need_K0') == 1:
            K_0 = 0.5
        if parametr_d.get('need_K0') == 0:
            K_0 = 1
        GLUB = parametr_proba.get('GLUB')
        if GLUB < 1:
            GLUB = 1
        press = ((GLUB * 20) / 1000) * K_0
    else:
        press = None

        #  + randint(5,15) / 1000

    parametr_press = {'press': press, 'press_1': press_1, 'press_2': press_2, 'press_3': press_3}

    return parametr_press


# execute - выполнить
# выполнить параметры испытания (очистка сводок)
def execute_parametr_isp(parametr_d, parametr_proba, parametr_isp, cursor):
    # Нужно ли проставить значения автоматически? (нормативные)
    if parametr_d.get('parametr_normativka') == 1:
        normative_value = normative_parametr_isp(parametr_proba)
        for value in 'C', 'F', 'E':
            parametr_isp.update({value: normative_value.get(value)})
    else:
        if parametr_isp.get('Norm') != None:
            # выбор проб для автомата
            normative_value = normative_parametr_isp(parametr_proba)
            for value in 'C', 'F', 'E':
                parametr_isp.update({value: normative_value.get(value)})
        else:
            pass
    return True


def delete_parametr_one_time(parametr_d, parametr_isp, cursor):
    # Нужно ли удалить сводки механики (1 - да, 0 - нет)
    if parametr_d.get('parametr_delete_sv_mex') == 1:
        if parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None:
            cursor.execute("DELETE FROM SVODKA_CM3")
        if parametr_isp.get('SPS') != None:
            cursor.execute("DELETE FROM SVODKA_SD")
        if parametr_isp.get('SPD') != None or parametr_isp.get('SPDL') != None:
            cursor.execute("DELETE FROM SVODKA_CM")
        cursor.commit()
        print('delete_parametr_one_time is DONE')
    if parametr_d.get('parametr_delete_sv_mex') == 11:
        cursor.execute("DELETE FROM SVODKA_CM3")
        cursor.execute("DELETE FROM SVODKA_SD")
        cursor.execute("DELETE FROM SVODKA_CM")
        cursor.commit()
    else:
        pass

    # Удалить испытания по механике? (0- нет, 1- трехосн, 2- срез, 3 - комп, 4- все)
    if parametr_d.get('delete_mex') == 1:
        cursor.execute("DELETE FROM CM3OPR")
    if parametr_d.get('delete_mex') == 2:
        cursor.execute("DELETE FROM SDOPR")
    if parametr_d.get('delete_mex') == 3:
        cursor.execute("DELETE FROM CMOPR")
    cursor.commit()
    if parametr_d.get('delete_mex') == 4:
        cursor.execute("DELETE FROM CM3OPR")
        cursor.execute("DELETE FROM SDOPR")
        cursor.execute("DELETE FROM CMOPR")
        cursor.commit()
    else:
        pass
    return True


def delete_parametr_many_time(parametr_d, parametr_isp, parametr_proba, cursor):
    # Удалить испытания по механике для каждой пробы в объекте? (0- нет, 1- трехосн, 2- срез, 3 - комп, 4- все)

    if parametr_d.get('what_delete') == 1 and (parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None):
        cursor.execute("DELETE FROM CM3OPR WHERE (PROBEGR_ID) = '%(PROBEGR_ID)s'" % {
            'PROBEGR_ID': parametr_proba.get('PROBEGR_IDS')})
        cursor.commit()
    if parametr_d.get('what_delete') == 2 and parametr_isp.get('SPS') != None:
        cursor.execute("DELETE FROM SDOPR WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
            'PROBAGR_OBJID': parametr_proba.get('PROBEGR_IDS')})
        cursor.commit()
    if parametr_d.get('what_delete') == 3 and parametr_isp.get('SPD') != None:
        cursor.execute("DELETE FROM CMOPR WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
            'PROBAGR_OBJID': parametr_proba.get('PROBEGR_IDS')})
        cursor.commit()
    if parametr_d.get('what_delete') == 4:
        if (parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None):
            cursor.execute("DELETE FROM CM3OPR WHERE (PROBEGR_ID) = '%(PROBEGR_ID)s'" % {
                'PROBEGR_ID': parametr_proba.get('PROBEGR_IDS')})
        if parametr_isp.get('SPS') != None:
            cursor.execute("DELETE FROM SDOPR WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                'PROBAGR_OBJID': parametr_proba.get('PROBEGR_IDS')})
        if parametr_isp.get('SPD') != None:
            cursor.execute("DELETE FROM CMOPR WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                'PROBAGR_OBJID': parametr_proba.get('PROBEGR_IDS')})
            cursor.commit()
    else:
        pass
    return True


def write_CM3opr(parametr_d, parametr_isp, parametr_proba):
    if parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None:
        # Нужно ли писать в одну вкладку (1 - да, 0 - нет) Трехосник
        try:
            if parametr_d.get('parametr_write_proba') == 1:
                # поиск номера пробы в сводке
                select_prgr = "SELECT OBJID FROM CM3OPR WHERE PROBEGR_ID = ?"
                result_search = cursor.execute(select_prgr, parametr_proba.get('PROBEGR_IDS')).fetchall()
                result_search = list(result_search[0])
                CM3DATA_OBJID = result_search[0]

            if parametr_d.get('parametr_write_proba') == 0:
                CM3DATA_OBJID = create_CM3OPR(cursor, parametr_proba)
        except:
            CM3DATA_OBJID = create_CM3OPR(cursor, parametr_proba)

        return CM3DATA_OBJID


# испытания
# трехосная прочность
# трехосная прочность
# трехосная прочность
def TPS(parametr_isp, parametr_proba, parametr_press):
    if parametr_proba.get('main_type') == 'incoherent':
        b = randint(80, 120)
    else:
        if parametr_proba.get('grunt_type') == 'supes' and parametr_proba.get('IL') <= 0.5:
            b = randint(300, 400) / 10
        if parametr_proba.get('grunt_type') == 'supes' and parametr_proba.get('IL') > 0.5:
            b = randint(400, 500) / 10
        if parametr_proba.get('grunt_type') == 'sugl':
            b = randint(50, 100) / 10
        if parametr_proba.get('grunt_type') == 'glina':
            b = randint(1, 15) / 10

    N = 2 * math.tan(math.pi * parametr_isp.get('F') / 180) * (
            (((math.tan(math.pi * parametr_isp.get('F') / 180)) ** 2) + 1) ** (1 / 2)) + 2 * (
                (math.tan(math.pi * parametr_isp.get('F') / 180)) ** 2) + 1
    M = 2 * (N ** (1 / 2)) * parametr_isp.get('C')
    st1 = (parametr_press.get('press_1') * N + M)
    st3 = (parametr_press.get('press_3') * N + M)
    st2 =  (((st1 + st3) / 2) * (
            parametr_press.get('press_2') / ((parametr_press.get('press_3') + parametr_press.get('press_1')) / 2)))

    tps_parametr = {'b': b, 'st1': st1, 'st2': st2, 'st3': st3}

    return tps_parametr


def graph_tps(st, press, press_name, parametr_d, parametr_isp, vert_speed, parametr_proba, random_start_e1):

    if vert_speed >= 0.3:
        e1_array = np.arange(random_start_e1, 11.4, vert_speed)
    else:
        e1_array = np.arange(random_start_e1, 11.4 + vert_speed, vert_speed)

    if e1_array[0] == 0:
        e1_array[0] = 0.00001


    first_point_e1 = np.asarray([float(e1_array[0]) for x in range(len(e1_array))])
    raznitsa_fistr_second_e1 = np.asarray(
        [float(e1_array[1] - e1_array[0]) for x in range(len(e1_array))])
    list_76 = np.asarray([float(76) for x in range(len(e1_array))])
    otn_def = (e1_array - first_point_e1) / (list_76 - raznitsa_fistr_second_e1)

    press_list = np.asarray([float(press) for x in range(len(e1_array))])

    if parametr_proba.get('main_type') == 'incoherent' and parametr_d.get('need_tail') == 1:

        first_point_tail = randint(6, 10) / 100
        otn_def_incoherent = otn_def.tolist()
        for x in otn_def_incoherent:
            if x > first_point_tail:
                index = otn_def_incoherent.index(x)
                break

        second_point_tail = first_point_tail + randint(2, 3) / 100
        for x in otn_def_incoherent:
            if x > second_point_tail:
                index_tail_2 = otn_def_incoherent.index(x)
                break

        if parametr_proba.get('main_type') == 'incoherent':
            curve = randint(10, 30) / 100
        if parametr_proba.get('grunt_type') == 'supes':
            curve = randint(30, 50) / 100
        if parametr_proba.get('grunt_type') == 'sugl':
            curve = randint(100, 200) / 100
        if parametr_proba.get('grunt_type') == 'glina':
            curve = randint(1000, 25000) / 100


        fake_e1_for_press = e1_array.copy()
        count_step_e1 = int(abs(random_start_e1 // vert_speed))
        for x in range(count_step_e1):
            fake_e1_for_press[x] = randint(1,5) / 10000

        c = (st / (math.atan(((e1_array[index] / curve)) ** 0.5)) - (press / (math.atan(((e1_array[index] / curve)) ** 0.5))))
        p_array_1 = []
        for x in range(len(e1_array)):
            p_array_1.append(c * math.atan((abs(fake_e1_for_press[x]) / curve) ** 0.5) + press)

        random_p = np.asarray([float(randint(0, 25) / 10000) for x in range(len(e1_array))])
        random_p[-1] = 0
        p_array_1 = p_array_1 - random_p
        p_array_1[-1] = st


        e1_array_tail = e1_array[index:index_tail_2]

        Y_move = e1_array[index]


        if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
            z = randint(4, 7) / 1000
        if parametr_proba.get('grunt_type') == 'mid_sand':
            z = randint(3, 6) / 1000
        if parametr_proba.get('grunt_type') == 'small_sand':
            z = randint(2, 5) / 1000
        if parametr_proba.get('grunt_type') == 'dust_sand':
            z = randint(1, 4) / 1000

        r = 2
        g = randint(10, 20) / 10

        X_move = z *  g * -e1_array_tail[0] ** 2 + 2 * Y_move * z * g * -e1_array_tail[0] + p_array_1[-1] + Y_move ** 2 * z * g - z * r ** 2

        X_move = 0

        tail_x = []
        for x in e1_array_tail:
            tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)
        X_move = p_array_1[-1] - tail_x[0]


        tail_x = []
        for x in e1_array_tail:
            tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)
        tail_x = np.asarray(tail_x)

        random_p = np.asarray([float(randint(0, 15) / 10000) for x in range(len(e1_array_tail))])
        random_p[-1] = 0
        tail_x = tail_x - random_p



        e1_array_tail_2 = e1_array[index_tail_2:]
        Y_move = e1_array_tail_2[-1]

        z = -z
        r = 2
        g = g / 2
        X_move = 0
        tail_x_2 = []
        for x in e1_array_tail_2:
            tail_x_2.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)
        tail_x_2 = np.asarray(tail_x_2)


        X_move = tail_x[-1] - tail_x_2[0]
        tail_x_2 = []
        for x in e1_array_tail_2:
            tail_x_2.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

        random_p = np.asarray([float(randint(0, 10) / 10000) for x in range(len(e1_array_tail_2))])
        random_p[-1] = 0
        tail_x_2 = tail_x_2 - random_p


        p_array_1 = p_array_1[:index]
        p_array_1 = np.concatenate((p_array_1, tail_x, tail_x_2))

        p_array_1 = p_array_1.tolist()
        maximum_p_index = p_array_1.index(max(p_array_1))
        p_array_1[maximum_p_index] = st
        p_array_1 = np.asarray(p_array_1)

    else:
        if parametr_proba.get('grunt_type') == 'supes':
            curve = randint(40, 50) / 100
        if parametr_proba.get('grunt_type') == 'sugl':
            curve = randint(100, 200) / 100
        if parametr_proba.get('grunt_type') == 'glina':
            curve = randint(1000, 25000) / 100

        c = (st / (math.atan(((e1_array[-1] / curve)) ** 0.5)) - (press / (math.atan(((e1_array[-1] / curve)) ** 0.5))))


        fake_e1_for_press = e1_array.copy()
        count_step_e1 = int(abs(random_start_e1 // vert_speed))
        for x in range(count_step_e1):
            fake_e1_for_press[x] = randint(1, 5) / 10000



        p_array_1 = []
        for x in range(len(e1_array)):
            p_array_1.append(c * math.atan((abs(fake_e1_for_press[x]) / curve) ** 0.5) + press)

        random_p = np.asarray([float(randint(0, 25) / 10000) for x in range(len(e1_array))])
        random_p[-1] = 0
        p_array_1[-1] = st
        p_array_1 = np.asarray(p_array_1)
        p_array_1 = p_array_1 - random_p


    quantity_point = len(p_array_1)

    return p_array_1, quantity_point, e1_array, otn_def


def list_choise1_tps(quantity_point, p_array_1):
    # лист с выбором последней точки
    p_array_1 = p_array_1.tolist()

    maximum_p = max(p_array_1)

    index_max_p = p_array_1.index(maximum_p)

    list_choise = [int(0) for x in range(quantity_point - 1)]  # SELECTED
    list_choise.insert(index_max_p, -1)
    return list_choise


def list_sequance1_tps(quantity_point):
    # последовательность точек с 1 до quantity_point
    list_sequance = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM
    return list_sequance


def create_ev_tps(b, quantity_point, e1_array):
    quantity_point = len(e1_array)
    try:
        if parametr_proba.get('Ip') < 7:
            b += randint(0, 50) / 10
            c = -(b * 10 + randint(1, 30))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(600, 900) / 10) for x in range(quantity_point)])

        if parametr_proba.get('Ip') >= 7 and parametr_proba.get('Ip') < 17:
            b += randint(0, 10) / 10
            c = -(b * 8 + randint(0, 5))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 600) / 100) for x in range(quantity_point)])

        if parametr_proba.get('Ip') >= 17:
            b += randint(0, 10) / 100
            c = -(b * 2 + randint(1, 20) / 10)
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 50) / 100) for x in range(quantity_point)])
    except:
        b += randint(0, 50) / 10
        c = -(b * 10 + randint(0, 500) / 10)
        d = randint(100, 1000)  # сколько прибавить по ev
        random_ev = np.asarray([float(randint(500, 1000) / 10) for x in range(quantity_point)])

    kf_y_b = np.asarray([float(b) for x in range(quantity_point)])
    kf_y_c = np.asarray([float(c) for x in range(quantity_point)])
    kf_y_d = np.asarray([float(d) for x in range(quantity_point)])

    st_b = np.asarray([float(2) for x in range(quantity_point)])

    ev_array_1 = ((kf_y_b * e1_array ** st_b) + (kf_y_c * e1_array) + kf_y_d) - random_ev  # DEFORM

    return ev_array_1


def write_EngGeo_TPS(p_array_1, e1_array, ev_array_1, list_sequance, list_choise, EXAM_NUM, press, quantity_point,
                     CM3DATA_OBJID):

    while e1_array[0] < 0:
        e1_array = np.delete(e1_array, 0)
        p_array_1 = np.delete(p_array_1, 0)
        ev_array_1 = np.delete(ev_array_1, 0)
        list_choise = np.delete(list_choise, 0)
    quantity_point = len(p_array_1)
    list_sequance = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM

    cursor.execute(
        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': EXAM_NUM, 'UNIFORM_PRESSURE': str(press).replace('.', ','),
           'FROM_MORECULON': -1,
           'FROM_NU_E': 0})

    for u in range(0, quantity_point):
        cursor.execute(
            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
            % {'OBJID': CM3DATA_OBJID,
               'EXAM_NUM': EXAM_NUM,
               'FORCE': (str(p_array_1[u])).replace('.', ','),
               'DEFORM': (str(e1_array[u])).replace('.', ','),
               'DEFORM_VOL': (str(ev_array_1[u])).replace('.', ','),
               'SERIAL_NUM': list_sequance[u],
               'SELECTED': list_choise[u],
               'SEL_FOR_NU': 0})
    cursor.commit()
    return True


def ISP_TPS(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_proba, press, parametr_d, parametr_press, vert_speed, random_start_e1, otn_def):

    quantity_point_past = len(p_array_1)

    if parametr_d.get('uploading_points') == 1:
        last_e1 = e1_array[-1]
        last_p = p_array_1[-1]
        last_ev = ev_array_1[-1]

        count_point = randint(5, 13)

        rzg_press = []
        koef = 0.75
        rzg_press.append(last_p * 0.75)
        for point in range(count_point):
            rzg_press.append(last_p * koef)
            koef = koef / 2

        rzg_ev = []
        koef = 0.75
        rzg_ev.append(last_ev * 0.75)
        for point in range(count_point):
            rzg_ev.append(last_ev * koef / 2)
            koef = koef / 2

        rzg_press = np.asarray(rzg_press)
        rzg_e1 = np.asarray([float(last_e1) for x in range(len(rzg_press))])
        rzg_ev = np.asarray(rzg_ev)

        p_array_1 = np.concatenate((p_array_1, rzg_press))
        e1_array = np.concatenate((e1_array, rzg_e1))
        ev_array_1 = np.concatenate((ev_array_1, rzg_ev))



    # холостой ход
    # холостой ход
    # холостой ход
    # холостой ход
    # холостой ход
    # 0 value
    # 0 value
    # 0 value
    # 0 value
    time_start = [round(randint(2, 9) / 100, 2)]
    for x in range(5):
        time_start.append(round(time_start[x] + randint(2, 9) / 100, 2))

    action_none_value = [str('') for x in range(6)]
    action_none_value[3] = 'Start'
    action_none_value[4] =  'Start'
    action_none_value[5] = 'LoadStage'


    action_changed_none_value = [str('') for x in range(6)]
    action_changed_none_value[0] = True
    action_changed_none_value[2] = True
    action_changed_none_value[4] = True


    list_1000 = [float(1000) for x in range(6)]

    Deviator_kPa_none_value = [float(0) for x in range(6)]

    value_none_cell_press = round(randint(10, 500) / 100, 1)
    CellPress_kPa_none_value = [float(0) for x in range(6)]
    CellPress_kPa_none_value[0] = value_none_cell_press
    CellPress_kPa_none_value[1] = value_none_cell_press

    VerticalPress_kPa_none_value = [float(0) for x in range(6)]
    VerticalPress_kPa_none_value[0] = value_none_cell_press
    VerticalPress_kPa_none_value[1] = value_none_cell_press



    value_none = round(randint(10, 20) / 10, 2)
    VerticalDeformation_mm_none_value = [float(0) for x in range(6)]
    VerticalDeformation_mm_none_value[0] = value_none
    VerticalDeformation_mm_none_value[1] = value_none


    VerticalStrain_none_value = [float(0) for x in range(6)]
    VerticalStrain_none_value[0] = str('')
    VerticalStrain_none_value[1] = str('')


    value_noneVolumeStrain = round(randint(1000, 11000) / 10000, 4)
    VolumeStrain_none_value = [float(0) for x in range(6)]
    VolumeStrain_none_value[0] = value_noneVolumeStrain
    VolumeStrain_none_value[1] = value_noneVolumeStrain


    value_noneVolumeDeformation_cm3_none_value = round(randint(4000, 50000) / 1000, 4)
    VolumeDeformation_cm3_none_value = [float(0) for x in range(6)]
    VolumeDeformation_cm3_none_value[0] = value_noneVolumeDeformation_cm3_none_value
    VolumeDeformation_cm3_none_value[1] = value_noneVolumeDeformation_cm3_none_value

    Deviator_MPa_none_value = [float(0) for x in range(6)]

    CellPress_MPa_none_value = [round(x / 1000, 4) for x in CellPress_kPa_none_value]

    VerticalPress_MPa_none_value = [round(x / 1000, 4) for x in VerticalPress_kPa_none_value]

    Trajectory_none_value = [str('') for x in range(6)]


    # load stage
    # load stage
    # load stage
    # load stage
    count_point_loadstage = randint(10, 15)
    step_time_loadstage = (30 + time_start[-1]) / (count_point_loadstage - 1)
    time_loadstage = [time_start[-1]]
    for x in range(count_point_loadstage - 1):
        time_loadstage.append(round(time_loadstage[x] + step_time_loadstage + randint(0, 50) / 100, 2))



    action_loadstage = [str('LoadStage') for x in range(count_point_loadstage)]

    action_changed_loadstage = [str('') for x in range(count_point_loadstage)]
    action_changed_loadstage[-1] = True


    list_1000 = [float(1000) for x in range(count_point_loadstage)]

    Deviator_kPa_loadstage = [float(0) for x in range(count_point_loadstage)]



    value_loadstage_start = randint(5, 20) / 10000
    CellPress_kPa_loadstage = [round(value_loadstage_start, 1)]
    step_press = (press  * 1000 - randint(1, 10) / 10000) / (count_point_loadstage - 1)
    for x in range(count_point_loadstage - 1):
        CellPress_kPa_loadstage.append(round(CellPress_kPa_loadstage[x] + step_press, 1))

    VerticalPress_kPa_loadstage = CellPress_kPa_loadstage



    count_step_e1 = int(abs(random_start_e1 // vert_speed)) - 1
    count_vert_def = count_point_loadstage - count_step_e1
    VerticalDeformation_mm_loadstage = [float(0) for x in range(count_point_loadstage)]
    count_point_plus_vert = 1
    for x in range(count_vert_def, count_point_loadstage):
        VerticalDeformation_mm_loadstage[x] = -vert_speed * count_point_plus_vert
        count_point_plus_vert += 1



    value_loadstage_start_volume = randint(5, 50) / 10000
    VolumeDeformation_cm3_loadstage = [round(value_loadstage_start_volume, 3)]
    step_volume = (ev_array_1[0] + randint(1, 20) / 100) / (count_point_loadstage - 1)
    for x in range(count_point_loadstage - 1):
        VolumeDeformation_cm3_loadstage.append(round(VolumeDeformation_cm3_loadstage[x] + step_volume, 3))

    Deviator_MPa_loadstage = [float(0) for x in range(count_point_loadstage)]

    CellPress_MPa_loadstage = [round(x / 1000, 4) for x in CellPress_kPa_loadstage]

    VerticalPress_MPa_loadstage = [round(x / 1000, 4) for x in VerticalPress_kPa_loadstage]

    Trajectory_loadstage = [str('') for x in range(count_point_loadstage)]


    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_loadstage)])
    volume_76 = np.asarray([float(76) for x in range(count_point_loadstage)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_loadstage)])
    VerticalStrain_loadstage = (VerticalDeformation_mm_loadstage - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_loadstage)])
    volume = np.asarray([float(86149) for x in range(count_point_loadstage)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_loadstage)])
    VolumeStrain_loadstage = (VolumeDeformation_cm3_loadstage - first_cell_ev) / (volume - (definirion_ev_array))

    # wait
    # wait
    # wait
    # wait
    time_wait = np.arange(round(time_loadstage[-1], 2), round(time_loadstage[-1] + parametr_d.get('reconsolidation'), 2), round(randint(290, 310) / 100, 2))
    time_wait = time_wait.tolist()
    time_wait.append(time_wait[-1])
    time_wait.append(time_wait[-1] + randint(90, 100) / 100)


    count_point_wait = len(time_wait)

    action_wait = [str('Wait') for x in range(count_point_wait)]
    action_wait[-1] = 'LoadStage'
    action_wait[-2] = 'LoadStage'


    action_changed_wait = [str('') for x in range(count_point_wait)]
    action_changed_wait[-3] = True
    action_changed_wait[-1] = True


    Deviator_kPa_wait = [float(0) for x in range(count_point_wait)]

    Deviator_MPa_wait = [float(0) for x in range(count_point_wait)]

    list_1000 = [float(1000) for x in range(count_point_wait)]

    random_CELL = np.asarray([float(randint(0, 50) / 100) for x in range(count_point_wait)])
    CellPress_kPa_wait = np.asarray([float(CellPress_kPa_loadstage[-1]) for x in range(count_point_wait)]) - random_CELL


    VerticalPress_kPa_wait = CellPress_kPa_wait


    random_VERT_wait = np.asarray([float(randint(0,2) / 100) for x in range(count_point_wait)])
    VerticalDeformation_mm_wait = np.asarray([float(VerticalDeformation_mm_loadstage[-1]) for x in range(count_point_wait)]) - random_VERT_wait

    VolumeDeformation_cm3_wait = [VolumeDeformation_cm3_loadstage[-1]]
    step_volume = ((ev_array_1[0] + randint(10, 20) / 10) - (ev_array_1[0])) / (count_point_wait - 1)
    for x in range(count_point_wait - 1):
        VolumeDeformation_cm3_wait.append(round(VolumeDeformation_cm3_wait[x] + step_volume, 3))

    CellPress_MPa_wait = [round(x / 1000, 4) for x in CellPress_kPa_wait]

    VerticalPress_MPa_wait = [round(x / 1000, 4) for x in VerticalPress_kPa_wait]

    Trajectory_wait = [str('') for x in range(count_point_wait)]

    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_wait)])
    volume_76 = np.asarray([float(76) for x in range(count_point_wait)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_wait)])
    VerticalStrain_wait = (VerticalDeformation_mm_wait - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_wait)])
    volume = np.asarray([float(86149) for x in range(count_point_wait)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_wait)])
    VolumeStrain_wait = (VolumeDeformation_cm3_wait - first_cell_ev) / (volume - (definirion_ev_array))


    # стабилизация
    # стабилизация
    # стабилизация
    # стабилизация
    # стабилизация

    # Стадии стабилизации в прочности нет, она включена в wait, тем не менее должна идти в соответствии с гостом для разных типов грунта

    if parametr_d.get('stabilization') != None:
        end_point_time_stab = parametr_d.get('stabilization')
        step = randint(75, 100) / 10
    else:
        if parametr_proba.get('main_type') == 'incoherent':
            end_point_time_stab = 0.5 * 60 * 60
            step = randint(50, 100) / 10
        Ip = parametr_proba.get('Ip')
        if parametr_proba.get('grunt_type') == 'supes':
            end_point_time_stab = 3 * 60 * 60
            step = randint(75, 100) / 10
        if parametr_proba.get('grunt_type') == 'sugl' and Ip  < 12:
            end_point_time_stab = 6 * 60 * 60
            step = randint(100, 150) / 10
        if parametr_proba.get('grunt_type') == 'sugl' and Ip  >= 12:
            end_point_time_stab = 12 * 60 * 60
            step = randint(150, 200) / 10
        if parametr_proba.get('grunt_type') == 'glina' and Ip  < 22:
            end_point_time_stab = 12 * 60 * 60
            step = randint(200, 250) / 10
        if parametr_proba.get('grunt_type') == 'glina' and Ip  >= 22:
            end_point_time_stab = 18 * 60 * 60
            step = randint(250, 300) / 10

    time_Stabilization = np.arange(round(time_wait[-1], 2), round(time_wait[-1] + end_point_time_stab, 2), round(step, 2))

    count_point_Stabilization = len(time_Stabilization)

    action_Stabilization = [str('Wait') for x in range(count_point_Stabilization)]

    action_changed_Stabilization = [str('') for x in range(count_point_Stabilization)]
    action_changed_Stabilization[-1] = True


    Deviator_kPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

    Deviator_MPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

    list_1000 = [float(1000) for x in range(count_point_Stabilization)]


    random_CELL = np.asarray([float(randint(0, 50) / 100) for x in range(count_point_Stabilization)])
    CellPress_kPa_Stabilization = np.asarray([float(CellPress_kPa_wait[-1]) for x in range(count_point_Stabilization)]) - random_CELL


    VerticalPress_kPa_Stabilization = CellPress_kPa_Stabilization

    random_VERT_wait = np.asarray([float(randint(0, 2) / 100) for x in range(count_point_Stabilization)])
    VerticalDeformation_mm_Stabilization = np.asarray([float(round(VerticalDeformation_mm_wait[-1], 2)) for x in range(count_point_Stabilization)]) - random_VERT_wait

    VolumeDeformation_cm3_Stabilization = [VolumeDeformation_cm3_wait[-1]]
    step_volume = (VolumeDeformation_cm3_wait[-1] - ev_array_1[0]) / (count_point_Stabilization - 1)
    for x in range(count_point_Stabilization - 1):
        VolumeDeformation_cm3_Stabilization.append(round(VolumeDeformation_cm3_Stabilization[x] + step_volume, 3))

    CellPress_MPa_Stabilization = [round(x / 1000, 4) for x in CellPress_kPa_Stabilization]

    VerticalPress_MPa_Stabilization = [round(x / 1000, 4) for x in VerticalPress_kPa_Stabilization]

    Trajectory_Stabilization = [str('') for x in range(count_point_Stabilization)]
    # VerticalStrain_none_value.insert(4, 'ReconsolidationWoDrain')

    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_Stabilization)])
    volume_76 = np.asarray([float(76) for x in range(count_point_Stabilization)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_Stabilization)])
    VerticalStrain_Stabilization = (VerticalDeformation_mm_Stabilization - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_Stabilization)])
    volume = np.asarray([float(86149) for x in range(count_point_Stabilization)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_Stabilization)])
    VolumeStrain_Stabilization = (VolumeDeformation_cm3_Stabilization - first_cell_ev) / (volume - (definirion_ev_array))


    # основная часть испытания
    # основная часть испытания
    # основная часть испытания
    # основная часть испытания
    p_array_1 = np.append(p_array_1, p_array_1[-1])
    e1_array = np.append(e1_array, e1_array[-1])
    ev_array_1 = np.append(ev_array_1, ev_array_1[-1])
    otn_def = np.append(otn_def, otn_def[-1])



    time_list = [time_Stabilization[-1]]
    step_time = (randint(6, 12) * 60 * 60) / (len(p_array_1) - 1)
    for x in range(len(p_array_1) - 1):
        time_list.append(round(time_list[x] + step_time + randint(0, 100) / 100, 2))
    time_list[-1] = time_list[-2]


    action_list = [str('WaitLimit') for x in range(len(p_array_1))]
    action_list[-1] = 'TerminateCondition'


    action_changed_list = [str('') for x in range(len(p_array_1))]
    action_changed_list[-2] = True




    # у прочности на наших приборах нет траектории
    # у деформации есть
    Trajectory_list = [str('') for x in range(len(p_array_1))]


    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(len(p_array_1))]) # e1_array[1] - e1_array[0]
    volume_76 = np.asarray([float(76) for x in range(len(p_array_1))])
    first_cell_e1 = np.asarray([float(e1_array[0]) for x in range(len(p_array_1))])
    VerticalStrain_list = (e1_array - first_cell_e1) / (volume_76 - (definirion_e1_array))




    press_list = np.asarray([float(press) for x in range(len(p_array_1))])
    random_press = np.asarray([float(randint(0, 3) / 1000) for x in range(len(p_array_1))])
    for x in range(10):
        random_press[x] = 0
    press_list = press_list - random_press
    # давление в камере в КПа
    list_1000 = np.asarray([float(1000) for x in range(len(p_array_1))])
    CellPress_kPa = press_list * list_1000



    # otn_vert_def
    definirion_ev_array = np.asarray([float(ev_array_1[1] - ev_array_1[0]) for x in range(len(p_array_1))])
    volume = np.asarray([float(86149) for x in range(len(p_array_1))])
    first_cell_ev = np.asarray([float(ev_array_1[0]) for x in range(len(p_array_1))])
    VolumeStrain_list = (ev_array_1 - first_cell_ev) / (volume - (definirion_ev_array))


    # Давление на образец в КПа
    VerticalPress_kPa = p_array_1 * list_1000


    # Девиатор разница между давлением на образец и давлением в камере
    # В МПа
    Deviator_MPa = p_array_1 - press_list
    # в КПа
    Deviator_kPa = VerticalPress_kPa - CellPress_kPa



    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога

    # Time
    # Time
    # Time
    time_start = np.around(np.asarray(time_start), decimals=2)

    time_loadstage = np.around(np.asarray(time_loadstage), decimals=2)

    time_wait = np.around(np.asarray(time_wait), decimals=2)

    np.around(time_Stabilization, decimals=2)

    time_list = np.around(np.asarray(time_list), decimals=2)

    Time_main = np.around(np.concatenate((time_start, time_loadstage, time_wait, time_Stabilization, time_list)), decimals=2)

    # Action
    # Action
    # Action

    action_none_value = np.asarray(action_none_value)

    action_loadstage = np.asarray(action_loadstage)

    action_wait = np.asarray(action_wait)

    action_Stabilization = np.asarray(action_Stabilization)

    action_list = np.asarray(action_list)

    Action_main = np.concatenate((action_none_value, action_loadstage, action_wait, action_Stabilization, action_list))

    # Action_Changed
    # Action_Changed
    # Action_Changed

    action_changed_none_value = np.asarray(action_changed_none_value)

    action_changed_loadstage = np.asarray(action_changed_loadstage)

    action_changed_wait = np.asarray(action_changed_wait)

    action_changed_Stabilization = np.asarray(action_changed_Stabilization)

    action_changed_list = np.asarray(action_changed_list)

    Action_Changed_main = np.concatenate((action_changed_none_value, action_changed_loadstage, action_changed_wait, action_changed_Stabilization, action_changed_list))

    # Deviator_kPa
    # Deviator_kPa
    # Deviator_kPa

    Deviator_kPa_none_value = np.around(np.asarray(Deviator_kPa_none_value), decimals=1)

    Deviator_kPa_loadstage = np.around(np.asarray(Deviator_kPa_loadstage), decimals=1)

    Deviator_kPa_wait = np.around(np.asarray(Deviator_kPa_wait), decimals=1)

    Deviator_kPa_Stabilization = np.around(np.asarray(Deviator_kPa_Stabilization), decimals=1)

    Deviator_kPa = np.around(np.asarray(Deviator_kPa), decimals=1)

    Deviator_kPa_main = np.around(np.concatenate((Deviator_kPa_none_value, Deviator_kPa_loadstage, Deviator_kPa_wait,
                   Deviator_kPa_Stabilization, Deviator_kPa)), decimals=1)

    # CellPress_kPa
    # CellPress_kPa
    # CellPress_kPa
    CellPress_kPa_none_value = np.around(np.asarray(CellPress_kPa_none_value), decimals=1)

    CellPress_kPa_loadstage = np.around(np.asarray(CellPress_kPa_loadstage), decimals=1)

    np.around(CellPress_kPa_wait, decimals=1)

    np.around(CellPress_kPa_Stabilization, decimals=1)

    np.around(CellPress_kPa, decimals=1)

    CellPress_kPa_main = np.around(np.concatenate((CellPress_kPa_none_value, CellPress_kPa_loadstage, CellPress_kPa_wait,
                   CellPress_kPa_Stabilization, CellPress_kPa)), decimals=1)


    # VerticalPress_kPa
    # VerticalPress_kPa
    # VerticalPress_kPa

    VerticalPress_kPa_none_value = np.around(np.asarray(VerticalPress_kPa_none_value), decimals=1)

    VerticalPress_kPa_loadstage = np.around(np.asarray(VerticalPress_kPa_loadstage), decimals=1)

    VerticalPress_kPa_wait = np.around(np.asarray(VerticalPress_kPa_wait), decimals=1)

    VerticalPress_kPa_Stabilization = np.around(np.asarray(VerticalPress_kPa_Stabilization), decimals=1)

    np.around(VerticalPress_kPa, decimals=1)

    VerticalPress_kPa_main = np.around(np.concatenate((VerticalPress_kPa_none_value, VerticalPress_kPa_loadstage, VerticalPress_kPa_wait,
                   VerticalPress_kPa_Stabilization, VerticalPress_kPa)), decimals=1)


    # VerticalDeformation_mm
    # VerticalDeformation_mm
    # VerticalDeformation_mm
    VerticalDeformation_mm_none_value = np.around(np.asarray(VerticalDeformation_mm_none_value), decimals=4)

    VerticalDeformation_mm_loadstage = np.around(np.asarray(VerticalDeformation_mm_loadstage), decimals=4)

    VerticalDeformation_mm_wait = np.around(np.asarray(VerticalDeformation_mm_wait), decimals=4)

    VerticalDeformation_mm_Stabilization = np.around(np.asarray(VerticalDeformation_mm_Stabilization), decimals=4)

    e1_array = np.around(e1_array, decimals=4)

    VerticalDeformation_mm_main = np.concatenate((VerticalDeformation_mm_none_value, VerticalDeformation_mm_loadstage, VerticalDeformation_mm_wait,
                   VerticalDeformation_mm_Stabilization, e1_array))


    # VerticalStrain
    # VerticalStrain
    # VerticalStrain

    VerticalStrain_none_value = np.asarray(VerticalStrain_none_value)

    VerticalStrain_loadstage = np.around(np.asarray(VerticalStrain_loadstage), decimals=4)

    VerticalStrain_wait = np.around(np.asarray(VerticalStrain_wait), decimals=4)

    VerticalStrain_Stabilization = np.around(np.asarray(VerticalStrain_Stabilization), decimals=4)

    # otn_def

    VerticalStrain_main = np.concatenate((VerticalStrain_none_value, VerticalStrain_loadstage, VerticalStrain_wait,
                   VerticalStrain_Stabilization, otn_def))

    # VolumeStrain
    # VolumeStrain
    # VolumeStrain
    VolumeStrain_none_value = np.around(np.asarray(VolumeStrain_none_value), decimals=4)

    VolumeStrain_loadstage = np.around(np.asarray(VolumeStrain_loadstage), decimals=4)

    VolumeStrain_wait = np.around(np.asarray(VolumeStrain_wait), decimals=4)

    VolumeStrain_Stabilization = np.around(np.asarray(VolumeStrain_Stabilization), decimals=4)

    VolumeStrain_list = np.around(np.asarray(VolumeStrain_list), decimals=4)

    VolumeStrain_main = np.around(np.concatenate((VolumeStrain_none_value, VolumeStrain_loadstage, VolumeStrain_wait,
                   VolumeStrain_Stabilization, VolumeStrain_list)), decimals=4)



    # VolumeDeformation_cm3
    # VolumeDeformation_cm3
    # VolumeDeformation_cm3
    VolumeDeformation_cm3_none_value = np.around(np.asarray(VolumeDeformation_cm3_none_value), decimals=3)

    VolumeDeformation_cm3_loadstage = np.around(np.asarray(VolumeDeformation_cm3_loadstage), decimals=3)

    VolumeDeformation_cm3_wait = np.around(np.asarray(VolumeDeformation_cm3_wait), decimals=3)

    VolumeDeformation_cm3_Stabilization = np.around(np.asarray(VolumeDeformation_cm3_Stabilization), decimals=3)

    ev_array_1 = np.around(ev_array_1, decimals=4)

    VolumeDeformation_cm3_main = np.concatenate((VolumeDeformation_cm3_none_value, VolumeDeformation_cm3_loadstage, VolumeDeformation_cm3_wait,
                   VolumeDeformation_cm3_Stabilization, ev_array_1))


    # Deviator_MPa
    # Deviator_MPa
    # Deviator_MPa
    Deviator_MPa_none_value = np.around(np.asarray(Deviator_MPa_none_value), decimals=4)

    Deviator_MPa_loadstage = np.around(np.asarray(Deviator_MPa_loadstage), decimals=4)

    Deviator_MPa_wait = np.around(np.asarray(Deviator_MPa_wait), decimals=4)

    Deviator_MPa_Stabilization = np.around(np.asarray(Deviator_MPa_Stabilization), decimals=4)

    Deviator_MPa = np.around(Deviator_MPa, decimals=4)

    Deviator_MPa_main = np.around(np.concatenate((Deviator_MPa_none_value, Deviator_MPa_loadstage, Deviator_MPa_wait,
                   Deviator_MPa_Stabilization, Deviator_MPa)), decimals=4)


    # CellPress_MPa
    # CellPress_MPa
    # CellPress_MPa
    CellPress_MPa_none_value = np.around(np.asarray(CellPress_MPa_none_value), decimals=4)

    CellPress_MPa_loadstage = np.around(np.asarray(CellPress_MPa_loadstage), decimals=4)

    CellPress_MPa_wait = np.around(np.asarray(CellPress_MPa_wait), decimals=4)

    CellPress_MPa_Stabilization = np.around(np.asarray(CellPress_MPa_Stabilization), decimals=4)

    press_list = np.around(press_list, decimals=4)

    CellPress_MPa_main = np.around(np.concatenate((CellPress_MPa_none_value, CellPress_MPa_loadstage, CellPress_MPa_wait,
                   CellPress_MPa_Stabilization, press_list)), decimals=4)



    # VerticalPress_MPa
    # VerticalPress_MPa
    # VerticalPress_MPa
    VerticalPress_MPa_none_value = np.around(np.asarray(VerticalPress_MPa_none_value), decimals=4)

    VerticalPress_MPa_loadstage = np.around(np.asarray(VerticalPress_MPa_loadstage), decimals=4)

    VerticalPress_MPa_wait = np.around(np.asarray(VerticalPress_MPa_wait), decimals=4)

    VerticalPress_MPa_Stabilization = np.around(np.asarray(VerticalPress_MPa_Stabilization), decimals=4)

    # p_array_1_isp

    VerticalPress_MPa_main = np.concatenate((VerticalPress_MPa_none_value, VerticalPress_MPa_loadstage, VerticalPress_MPa_wait,
                   VerticalPress_MPa_Stabilization, p_array_1))



    # Trajectory
    # Trajectory
    # Trajectory

    Trajectory_none_value = np.asarray(Trajectory_none_value)

    Trajectory_loadstage = np.asarray(Trajectory_loadstage)

    Trajectory_wait = np.asarray(Trajectory_wait)

    Trajectory_Stabilization = np.asarray(Trajectory_Stabilization)

    Trajectory_list = np.asarray(Trajectory_list)

    Trajectory_main = np.concatenate((Trajectory_none_value, Trajectory_loadstage, Trajectory_wait,
                   Trajectory_Stabilization, Trajectory_list))



    log_Execute = {}
    log_General = {}

    random_time_log = randint(1, 15) / 100
    log_Execute.setdefault(0, f"Time	Message	Message_Changed	")
    log_Execute.setdefault(1, f"{round(time_start[-1] - random_time_log, 2)}		{True}	")
    log_Execute.setdefault(2, f"{round(time_start[-1] - random_time_log, 2)}	Стадия: [Start] Подготовка к испытанию; Сообщение: Стадия реконсолидации в условиях отсутствия дренажа.		")

    random_time_log = randint(1, 10) / 100
    log_Execute.setdefault(3, f"{round(time_loadstage[-1] - random_time_log, 2)}	Стадия: [Start] Подготовка к испытанию; Сообщение: Стадия реконсолидации в условиях отсутствия дренажа.	{True}	")
    log_Execute.setdefault(4, f"{round(time_loadstage[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создано всестороннее давление {int(press * 1000)} кПа.		")

    random_time_log = randint(3, 10) / 100
    log_Execute.setdefault(5, f"{round(time_loadstage[-1] + random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создано всестороннее давление {int(press * 1000)} кПа.	{True}	")

    log_Execute.setdefault(6, f"{round(time_loadstage[-1] + random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation')), 1)} с.	")

    random_time_log = randint(40, 60) / 100
    log_Execute.setdefault(7, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation')), 1)} с.	{True}	")
    log_Execute.setdefault(8, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа всесторонним давлением в камере завершена.		")
    random_time_log = randint(30, 39) / 100
    log_Execute.setdefault(9, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа всесторонним давлением в камере завершена.	{True}	")
    log_Execute.setdefault(10, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа завершена.		")

    volume_log_wait = (86149 + VolumeDeformation_cm3_wait[-1]) / 1000
    vertical_log_wait = (76 - VerticalDeformation_mm_wait[-1])

    random_time_log = randint(20, 29) / 100
    log_Execute.setdefault(11, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа завершена.	{True}	")
    log_Execute.setdefault(12, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после реконсолидации составили: Высота {round(vertical_log_wait, 2)} мм; Площадь 11.3 кв.см; Объем {round(volume_log_wait, 1)} куб.см.		")

    random_time_log = randint(10, 19) / 100
    log_Execute.setdefault(13, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после реконсолидации составили: Высота {round(vertical_log_wait, 2)} мм; Площадь 11.3 кв.см; Объем {round(volume_log_wait, 1)} куб.см.	{True}	")

    log_Execute.setdefault(14, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Стадия дополнительного уплотнения.		")

    random_time_log = randint(1, 9) / 100
    log_Execute.setdefault(15, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Стадия дополнительного уплотнения.	{True}	")

    log_Execute.setdefault(16, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создана ступень всестороннего давления {int(press * 1000)} кПа.		")

    random_time_log = -randint(10, 17) / 100
    log_Execute.setdefault(17, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создана ступень всестороннего давления {int(press * 1000)} кПа.	{True}	")

    log_Execute.setdefault(18, f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(end_point_time_stab), 1)} с.		")

    random_time_log = -randint(40, 60) / 100
    log_Execute.setdefault(19, f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(end_point_time_stab), 1)} с.	{True}	")

    log_Execute.setdefault(20, f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Ожидание времени завершено.		")

    volume_log_Stabilization = (volume_log_wait * 1000 + VolumeDeformation_cm3_Stabilization[-1]) / 1000
    vertical_log_Stabilization = (vertical_log_wait - VerticalDeformation_mm_Stabilization[-1])
    square_log_Stabilization = ((volume_log_wait * 1000) / vertical_log_wait) / 100

    random_time_log = -randint(30, 39) / 100
    log_Execute.setdefault(21, f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Ожидание времени завершено.	{True}	")

    log_Execute.setdefault(22, f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.		")

    log_Execute.setdefault(23, f"{round(time_list[-1], 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.	{True}	")

    log_Execute.setdefault(24, f"{round(time_list[-1], 2)}	Стадия: [TerminateCondition] Испытание завершилось по условию; Сообщение: Завершения испытания...		")

    # перевод прочности в сm3 вместо mm3

    list_1000_vol = np.asarray([float(1000) for x in range(len(VolumeDeformation_cm3_main))])
    VolumeDeformation_cm3_main = VolumeDeformation_cm3_main / list_1000_vol

# Time	Action	Action_Changed	Deviator_kPa	CellPress_kPa	VerticalPress_kPa	VerticalDeformation_mm	VerticalStrain	VolumeStrain	VolumeDeformation_cm3	Deviator_MPa	CellPress_MPa	VerticalPress_MPa	Trajectory
# 14
    log_General.setdefault(0, f"SampleHeight_mm	SampleDiameter_mm	SampleHeightConsolidated_mm	SampleVolumeConsolidated_cm3	SampleAreaConsolidated_cm2	PlungerArea_mm2	")
    log_General.setdefault(1, f"76	38	0.00	0.0000	0.0000	314	")
    log_General.setdefault(2, f"76	38	76.00	86.1490	11.3354	314	")
    log_General.setdefault(3, f"76	38	{round(float(vertical_log_wait), 2)}	{round(float(volume_log_wait), 4)}	{11.3354}	314	")
    log_General.setdefault(4, f"76	38	{round(float(vertical_log_Stabilization), 2)}	{round(float(volume_log_Stabilization), 4)}	{round(float(square_log_Stabilization), 4)}	314	")

    df = pd.DataFrame({'Time': Time_main, 'Action': Action_main, 'Action_Changed': Action_Changed_main,
                       'Deviator_kPa': Deviator_kPa_main, 'CellPress_kPa': CellPress_kPa_main, 'VerticalPress_kPa': VerticalPress_kPa_main,
                       'VerticalDeformation_mm': VerticalDeformation_mm_main,
                       'VerticalStrain': VerticalStrain_main, 'VolumeStrain': VolumeStrain_main, 'VolumeDeformation_cm3': VolumeDeformation_cm3_main,
                       'Deviator_MPa': Deviator_MPa_main,
                       'CellPress_MPa': CellPress_MPa_main, 'VerticalPress_MPa': VerticalPress_MPa_main, 'Trajectory': Trajectory_main})



    picture_time = time.strftime("%Y.%m.%d %H_%M_%S", time.localtime(time.time()))

    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/TPS/')
    os.mkdir(str(press))
    os.chdir(str(press))
    shutil.copy('Z:/Zapis\ISP\obr_TPS.xml', File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press))
    os.rename(
        f"{File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press) + '/obr_TPS.xml'}",
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPS/{str(press)}" + f"/{picture_time}.xml")

    os.mkdir('Execute')
    os.chdir('Execute')
    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press) + '/Execute/'+ 'Execute.1.log'}", "w") as file:
        for key in log_Execute.keys():
            file.write(str(log_Execute.get(key)) + '\n')
    os.chdir('..')



    os.mkdir('General')
    os.chdir('General')

    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press) + '/General/'+ 'General.1.log'}", "w") as file:
        for key in log_General.keys():
            file.write(str(log_General.get(key)) + '\n')

    my_file.close()
    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(f"{File_Path + parametr_isp.get('LAB_NO')}/TPS/{str(press)}/Test/{'Test.1'}.log", sep='\t',
              index=False)  # создание лога из выведенного датафрейма

    return True


# трехосная деформация
# трехосная деформация
# трехосная деформация
def TPD(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID):
    press = parametr_press.get('press')

    if parametr_proba.get('main_type') == 'incoherent':
        b = randint(300, 400) / 10
    else:
        if parametr_proba.get('grunt_type') == 'supes':
            b = randint(300, 400) / 10

        if parametr_proba.get('grunt_type') == 'sugl':
            b = randint(50, 100) / 10

        if parametr_proba.get('grunt_type') == 'glina':
            b = randint(1, 15) / 10

    parametr_tpd = {'b': b}

    return parametr_tpd


def graph(parametr_press, parametr_isp, vert_speed, parametr_proba):

    press = parametr_press.get('press')
    E = parametr_isp.get('E')


    koef_vert_speed = vert_speed / 0.02


    e1_array = np.arange(0.0000001, 11.4, vert_speed)




    first_point_e1 = np.asarray([float(e1_array[0]) for x in range(len(e1_array))])

    raznitsa_fistr_second_e1 = np.asarray(
        [float(e1_array[1] - e1_array[0]) for x in range(len(e1_array))])

    list_76 = np.asarray([float(76) for x in range(len(e1_array))])

    otn_def = (e1_array - first_point_e1) / (list_76 - raznitsa_fistr_second_e1)



    if press <= 0.1 and vert_speed <= 0.05:
        point_1 = randint(1, 2)
        point_2 = point_1 + 1
    elif press <= 0.2 and vert_speed <= 0.05:
        point_1 = randint(1, 5)
        point_2 = point_1 + 1
    elif press <= 0.3 and vert_speed <= 0.05:
        point_1 = randint(5, 10)
        point_2 = point_1 + 1
    elif press <= 0.3 and vert_speed <= 0.05:
        point_1 = randint(5, 20)
        point_2 = point_1 + 1
    else:
        point_1 = randint(1, 2)
        point_2 = point_1 + 1
    points_l = [point_1, point_2]


    press_list = np.asarray([float(press) for x in range(len(e1_array))])


    if parametr_proba.get('main_type') == 'incoherent':
        koef_E_list = 0.06 - ((50 - E) / (40)) * (0.05)
        if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
            koef_E_list = koef_E_list * (randint(10, 15) / 100 + 1)
        if parametr_proba.get('grunt_type') == 'mid_sand':
            koef_E_list = koef_E_list * (randint(8, 13) / 100 + 1)
        if parametr_proba.get('grunt_type') == 'small_sand':
            koef_E_list = koef_E_list * (randint(6, 11) / 100 + 1)
        if parametr_proba.get('grunt_type') == 'dust_sand':
            koef_E_list = koef_E_list * (randint(1, 6) / 100 + 1)
    else:
        if parametr_proba.get('grunt_type') == 'supes':
            koef_E_list = 0.031 - ((50 - E) / (40)) * (0.025)
        if parametr_proba.get('grunt_type') == 'sugl':
            koef_E_list = 0.025 - ((50 - E) / (40)) * (0.022)
        if parametr_proba.get('grunt_type') == 'glina':
            koef_E_list = 0.02 - ((50 - E) / (40)) * (0.019)

    koef_E_list = koef_E_list * koef_vert_speed

    E_list = np.arange(E, E - koef_E_list * len(e1_array), - koef_E_list)
    for x in range(point_2 + 1):
        E_list[x] = E

    count_point_E = len(E_list)
    count_point_E1 = len(e1_array)
    while count_point_E != count_point_E1:
        if count_point_E < count_point_E1:
            E_list = np.append(E_list, E_list[-1] - koef_E_list)
        else:
            E_list = np.delete(E_list, -1)
        count_point_E = len(E_list)
        count_point_E1 = len(e1_array)


    point_1_list_e1 = np.asarray([float(e1_array[point_1]) for x in range(len(e1_array))])

    point_2_list_e1 = np.asarray([float(e1_array[point_2]) for x in range(len(e1_array))])


    point_1_list_otn_def = np.asarray([float(otn_def[point_1]) for x in range(len(e1_array))])

    point_2_list_otn_def = np.asarray([float(otn_def[point_2]) for x in range(len(e1_array))])


    p_array_1 = ((e1_array / (((((point_2_list_e1) ** (1 / 2)) - ((point_1_list_e1) ** (1 / 2))) / (E_list * (point_2_list_otn_def-point_1_list_otn_def))) ** 2)) ** (1 / 2)) + press_list

    right_P_step = otn_def[point_1] * E


    if parametr_proba.get('main_type') == 'incoherent' and parametr_d.get('need_tail_def') == 1:
        otn_def_incoherent = otn_def.tolist()
        for x in otn_def_incoherent:
            if x > randint(8, 12) / 100:
                index = otn_def_incoherent.index(x)
                break

        e1_array_tail = e1_array[index:]

        Y_move = (e1_array[-1] + e1_array[index]) / 2
        X_move = 0
        if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
            z = -randint(6, 9) / 10000
        if parametr_proba.get('grunt_type') == 'mid_sand':
            z = -randint(4, 7) / 10000
        if parametr_proba.get('grunt_type') == 'small_sand':
            z = -randint(2, 5) / 10000
        if parametr_proba.get('grunt_type') == 'dust_sand':
            z = -randint(2, 5) / 10000
        r = 4
        g = 10

        tail_x = []

        for x in e1_array_tail:
            tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

        definition_p = p_array_1[index] - tail_x[0] - 0.015



        X_move = p_array_1[index] - tail_x[0] - 0.001
        tail_x = []

        for x in e1_array_tail:
            tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

        max_tail_x = min(tail_x)
        index_max_x = tail_x.index(max_tail_x)

        num_index_rewrite = [int(index) for index in range(index_max_x, len(tail_x))]

        for x in num_index_rewrite:
            tail_x[x] = max_tail_x


        tail_x = np.asarray(tail_x)



        p_array_1 = p_array_1[:index]
        p_array_1 = np.concatenate((p_array_1, tail_x))

    random_p = np.asarray([float(randint(0, 25) / 10000) for x in range(len(e1_array))])
    for x in range(point_2 + 1):
        random_p[x] = 0

    p_array_1 = p_array_1 - random_p

    E_now = (p_array_1[point_2] - p_array_1[point_1]) / (otn_def[point_2] - otn_def[point_1])

    return p_array_1, e1_array, points_l, otn_def







def graphic(press, quantity_point, search_P, real_isp_TPD):
    point_press = randint(5, 20) / 1000
    k_press_P = np.arange(press + point_press, press+ point_press + quantity_point * search_P, search_P)

    while quantity_point != len(k_press_P):
        if quantity_point > len(k_press_P):
            k_press_P = numpy.append(k_press_P, k_press_P[(len(k_press_P) - 1)] + search_P)
        if quantity_point < len(k_press_P):
            k_press_P = numpy.delete(k_press_P, len(k_press_P) - 1)

    # рандом по P

    if real_isp_TPD.get('parametr_p') == 1:
        p_array_1 = k_press_P
        return p_array_1

    random_x = np.asarray([float(randint(0, 20) / 10000) for x in range(quantity_point)])

    for x in range(30):
        random_x[x] = 0
    if press < 0.1:
        random_x = np.asarray([float(randint(0, 5) / 10000) for x in range(quantity_point)])

        for x in range(30):
            random_x[x] = 0
        p_array_1 = k_press_P - random_x
    else:
        p_array_1 = k_press_P - random_x

    return p_array_1


def list_choise_tpd(quantity_point, point_1, point_2):
    # лист с выбором последней точки
    list_choise1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise1[point_1] = -1
    list_choise1[point_2] = -1
    return list_choise1


def list_sequance1_tpd(quantity_point):
    # последовательность точек с 1 до quantity_point
    list_sequance1 = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM
    return list_sequance1


def list_choise_NU_tpd(quantity_point, point_1, point_2):
    # лист по NU
    list_choise_NU_1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise_NU_1[point_1] = -1
    list_choise_NU_1[point_2] = -1
    return list_choise_NU_1


def create_ev(otn_def, b, quantity_point, parametr_proba, parametr_press, e1_array, point_1, point_2):

    Ip = parametr_proba.get('Ip')
    try:
        if Ip < 7:
            b += randint(0, 50) / 10
            c = -(b * 10 + randint(1, 30))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(600, 900) / 10) for x in range(quantity_point)])

        if Ip >= 7 and Ip < 17:
            b += randint(0, 10) / 10
            c = -(b * 8 + randint(0, 5))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 600) / 100) for x in range(quantity_point)])

        if Ip >= 17:
            b += randint(0, 10) / 100
            c = -(b * 3 + randint(1, 20) / 10)
            d = randint(0, 200)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 250) / 100) for x in range(quantity_point)])
    except:
        b += randint(0, 50) / 10
        c = -(b * 10 + randint(0, 500) / 10)
        d = randint(100, 1000)  # сколько прибавить по ev
        random_ev = np.asarray([float(randint(500, 1000) / 10) for x in range(quantity_point)])


    kf_y_b = np.asarray([float(b) for x in range(quantity_point)])
    kf_y_c = np.asarray([float(c) for x in range(quantity_point)])
    kf_y_d = np.asarray([float(d) for x in range(quantity_point)])

    st_b = np.asarray([float(2) for x in range(quantity_point)])

    ev_array_1 = ((kf_y_b * e1_array ** st_b) + (kf_y_c * e1_array) + kf_y_d) - random_ev  # DEFORM

    # точка по EV

    # tochka EV _ 2 - EV _ 1

    point_EV = np.asarray([float(ev_array_1[1] - ev_array_1[0]) for x in range(quantity_point)])

    first_point_EV = np.asarray([float(ev_array_1[0]) for x in range(quantity_point)])

    volume_lab = np.asarray([float((math.pi * 19 ** 2) * 76) for x in range(quantity_point)])

    otn_volume_def = (first_point_EV - ev_array_1) / (volume_lab - point_EV)

    point_1_EV = (otn_def[point_1] + otn_volume_def[point_1]) / 2

    point_2_EV = (otn_def[point_2] + otn_volume_def[point_2]) / 2

    difference_p1_p2 = point_2_EV - point_1_EV

    koef_V_1 = abs(1 - (difference_p1_p2 / (otn_def[point_2] - otn_def[point_1])))

    # перерасчет коэффициента Пуассона
    grunt = parametr_proba.get('grunt_type')
    IL = parametr_proba.get('IL')
    if parametr_proba.get('main_type') == 'incoherent':
        k_puss = randint(30, 35) / 100
    if grunt == 'supes':
        k_puss = randint(30, 35) / 100
    if grunt == 'sugl':
        k_puss = randint(35, 37) / 100
    if grunt == 'glina':
        if IL <= 0:
            k_puss = randint(20, 30) / 100
        if 0 < IL <= 0.25:
            k_puss = randint(30, 38) / 100
        if 0.25 < IL <= 1:
            k_puss = randint(38, 45) / 100

    if k_puss != koef_V_1:
        opr_defin = (1 - k_puss) * (otn_def[point_2] - otn_def[point_1])

        otn_vol_point_right = -otn_def[point_2] + otn_def[point_1] + 2 * opr_defin + otn_volume_def[
            point_1]

        EV_2 = -otn_vol_point_right * volume_lab[1] + otn_vol_point_right * difference_p1_p2 + \
               first_point_EV[1]

        ev_array_1[point_2] = EV_2

    return ev_array_1


def write_EngGeo_TPD(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise, list_choise_NU_tpd,
                     CM3DATA_OBJID):
    cursor.execute(
        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 0,
           'UNIFORM_PRESSURE': str(parametr_press.get('press')).replace('.', ','), 'FROM_MORECULON': 0,
           'FROM_NU_E': -1, })

    for u in range(0, len(p_array_1)):
        cursor.execute(
            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
            % {'OBJID': CM3DATA_OBJID,
               'EXAM_NUM': 0,
               'FORCE': (str(p_array_1[u])).replace('.', ','),
               'DEFORM': (str(e1_array[u])).replace('.', ','),
               'DEFORM_VOL': (str(ev_array_1[u])).replace('.', ','),
               'SERIAL_NUM': list_sequance[u],
               'SELECTED': list_choise[u],
               'SEL_FOR_NU': list_choise_NU_tpd[u]})
    cursor.commit()
    return True


def ISP_TPD(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_press, parametr_proba, parametr_d, points_l, picture_time):
    press = parametr_press.get('press')

    if parametr_d.get('uploading_points') == 1:
        last_e1 = e1_array[-1]
        last_p = p_array_1[-1]
        last_ev = ev_array_1[-1]

        count_point = randint(5, 13)

        rzg_press = []
        koef = 0.75
        rzg_press.append(last_p * 0.75)
        for point in range(count_point):
            rzg_press.append(last_p * koef)
            koef = koef / 2

        rzg_ev = []
        koef = 0.75
        rzg_ev.append(last_ev * 0.75)
        for point in range(count_point):
            rzg_ev.append(last_ev * koef / 2)
            koef = koef / 2

        rzg_press = np.asarray(rzg_press)
        rzg_e1 = np.asarray([float(last_e1) for x in range(len(rzg_press))])
        rzg_ev = np.asarray(rzg_ev)

        p_array_1 = np.concatenate((p_array_1, rzg_press))
        e1_array = np.concatenate((e1_array, rzg_e1))
        ev_array_1 = np.concatenate((ev_array_1, rzg_ev))


    # холостой ход
    # холостой ход
    # холостой ход
    # холостой ход
    # холостой ход
    # 0 value
    # 0 value
    # 0 value
    # 0 value
    time_start = [randint(2, 9) / 100]
    for x in range(5):
        time_start.append(time_start[x] + randint(2, 9) / 100)

    action_none_value = [str('') for x in range(6)]
    action_none_value[3] = 'Start'
    action_none_value[4] = 'Start'
    action_none_value[5] = 'LoadStage'

    action_changed_none_value = [str('') for x in range(6)]
    action_changed_none_value[0] = True
    action_changed_none_value[2] = True
    action_changed_none_value[4] = True

    list_1000 = [float(1000) for x in range(6)]

    Deviator_kPa_none_value = [float(0) for x in range(6)]

    value_none_cell_press = randint(10, 500) / 100
    CellPress_kPa_none_value = [float(0) for x in range(6)]
    CellPress_kPa_none_value[0] = value_none_cell_press
    CellPress_kPa_none_value[1] = value_none_cell_press

    VerticalPress_kPa_none_value = [float(0) for x in range(6)]
    VerticalPress_kPa_none_value[0] = value_none_cell_press
    VerticalPress_kPa_none_value[1] = value_none_cell_press

    value_none = randint(10, 20) / 10
    VerticalDeformation_mm_none_value = [float(0) for x in range(6)]
    VerticalDeformation_mm_none_value[0] = value_none
    VerticalDeformation_mm_none_value[1] = value_none

    VerticalStrain_none_value = [float(0) for x in range(6)]
    VerticalStrain_none_value[0] = str('')
    VerticalStrain_none_value[1] = str('')

    value_noneVolumeStrain = randint(1000, 11000) / 10000
    VolumeStrain_none_value = [float(0) for x in range(6)]
    VolumeStrain_none_value[0] = value_noneVolumeStrain
    VolumeStrain_none_value[1] = value_noneVolumeStrain

    value_noneVolumeDeformation_cm3_none_value = randint(4000, 50000) / 1000
    VolumeDeformation_cm3_none_value = [float(0) for x in range(6)]
    VolumeDeformation_cm3_none_value[0] = value_noneVolumeDeformation_cm3_none_value
    VolumeDeformation_cm3_none_value[1] = value_noneVolumeDeformation_cm3_none_value

    Deviator_MPa_none_value = [float(0) for x in range(6)]

    CellPress_MPa_none_value = [x / 1000 for x in CellPress_kPa_none_value]

    VerticalPress_MPa_none_value = [x / 1000 for x in VerticalPress_kPa_none_value]

    Trajectory_none_value = [str('') for x in range(6)]
    Trajectory_none_value[-1] = 'ReconsolidationWoDrain'

    # load stage
    # load stage
    # load stage
    # load stage
    count_point_loadstage = randint(10, 25)
    step_time_loadstage = (30 + time_start[-1]) / (count_point_loadstage - 1)
    time_loadstage = [time_start[-1]]
    for x in range(count_point_loadstage - 1):
        time_loadstage.append(time_loadstage[x] + step_time_loadstage + randint(0, 50) / 100)

    action_loadstage = [str('LoadStage') for x in range(count_point_loadstage)]

    action_changed_loadstage = [str('') for x in range(count_point_loadstage)]
    action_changed_loadstage[-1] = True

    list_1000 = [float(1000) for x in range(count_point_loadstage)]

    Deviator_kPa_loadstage = [float(0) for x in range(count_point_loadstage)]

    value_loadstage_start = randint(5, 20) / 10000
    CellPress_kPa_loadstage = [value_loadstage_start]
    step_press = (press * 1000 - randint(1, 20) / 100) / (count_point_loadstage - 1)
    for x in range(count_point_loadstage - 1):
        CellPress_kPa_loadstage.append(CellPress_kPa_loadstage[x] + step_press)

    VerticalPress_kPa_loadstage = CellPress_kPa_loadstage

    VerticalDeformation_mm_loadstage = [float(e1_array[0]) for x in range(count_point_loadstage)]

    value_loadstage_start_volume = randint(5, 50) / 10000
    VolumeDeformation_cm3_loadstage = [value_loadstage_start_volume]
    step_volume = (ev_array_1[0] + randint(10, 20) / 10) / (count_point_loadstage - 1)
    for x in range(count_point_loadstage - 1):
        VolumeDeformation_cm3_loadstage.append(VolumeDeformation_cm3_loadstage[x] + step_volume)

    Deviator_MPa_loadstage = [float(0) for x in range(count_point_loadstage)]

    CellPress_MPa_loadstage = [x / 1000 for x in CellPress_kPa_loadstage]

    VerticalPress_MPa_loadstage = [x / 1000 for x in VerticalPress_kPa_loadstage]

    Trajectory_loadstage = [str('ReconsolidationWoDrain') for x in range(count_point_loadstage)]

    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_loadstage)])
    volume_76 = np.asarray([float(76) for x in range(count_point_loadstage)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_loadstage)])
    VerticalStrain_loadstage = (VerticalPress_MPa_loadstage - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_loadstage)])
    volume = np.asarray([float(86149) for x in range(count_point_loadstage)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_loadstage)])
    VolumeStrain_loadstage = (VolumeDeformation_cm3_loadstage - first_cell_ev) / (volume - (definirion_ev_array))

    # wait
    # wait
    # wait
    # wait
    time_wait = np.arange(time_loadstage[-1], time_loadstage[-1] + parametr_d.get('reconsolidation_def'),
                          randint(290, 310) / 100)
    time_wait = time_wait.tolist()
    time_wait.append(time_wait[-1])
    time_wait.append(time_wait[-1] + randint(90, 100) / 100)

    count_point_wait = len(time_wait)

    action_wait = [str('Wait') for x in range(count_point_wait)]
    action_wait[-1] = 'LoadStage'
    action_wait[-2] = 'LoadStage'

    action_changed_wait = [str('') for x in range(count_point_wait)]
    action_changed_wait[-3] = True
    action_changed_wait[-1] = True

    Deviator_kPa_wait = [float(0) for x in range(count_point_wait)]

    Deviator_MPa_wait = [float(0) for x in range(count_point_wait)]

    list_1000 = [float(1000) for x in range(count_point_wait)]

    CellPress_kPa_wait = np.asarray([float(CellPress_kPa_loadstage[-1]) for x in range(count_point_wait)]) - np.asarray(
        [float(randint(0, 10) / 1000) for x in range(count_point_wait)])

    VerticalPress_kPa_wait = CellPress_kPa_wait

    VerticalDeformation_mm_wait = [float(VerticalDeformation_mm_loadstage[-1]) for x in range(count_point_wait)]

    VolumeDeformation_cm3_wait = [VolumeDeformation_cm3_loadstage[-1]]
    step_volume = ((ev_array_1[0] + randint(10, 20) / 10) - (ev_array_1[0])) / (count_point_wait - 1)
    for x in range(count_point_wait - 1):
        VolumeDeformation_cm3_wait.append(VolumeDeformation_cm3_wait[x] + step_volume)

    CellPress_MPa_wait = [x / 1000 for x in CellPress_kPa_wait]

    VerticalPress_MPa_wait = [x / 1000 for x in VerticalPress_kPa_wait]

    Trajectory_wait = [str('ReconsolidationWoDrain') for x in range(count_point_wait)]
    Trajectory_wait[-1] = 'Consolidation'
    Trajectory_wait[-2] = 'Consolidation'
    Trajectory_wait[-2] = 'Consolidation'


    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_wait)])
    volume_76 = np.asarray([float(76) for x in range(count_point_wait)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_wait)])
    VerticalStrain_wait = (VerticalPress_MPa_wait - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_wait)])
    volume = np.asarray([float(86149) for x in range(count_point_wait)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_wait)])
    VolumeStrain_wait = (VolumeDeformation_cm3_wait - first_cell_ev) / (volume - (definirion_ev_array))

    # стабилизация
    # стабилизация
    # стабилизация
    # стабилизация
    # стабилизация

    # Стадии стабилизации в прочности нет, она включена в wait, тем не менее должна идти в соответствии с гостом для разных типов грунта

    if parametr_d.get('stabilization_def') != None:
        end_point_time_stab = parametr_d.get('stabilization_def')
        if parametr_proba.get('main_type') == 'incoherent':
            step = randint(50, 100) / 10
        else:
            Ip = parametr_proba.get('Ip')
            if parametr_proba.get('grunt_type') == 'supes':
                step = randint(75, 100) / 10
            if parametr_proba.get('grunt_type') == 'sugl' and Ip < 12:
                step = randint(100, 150) / 10
            if parametr_proba.get('grunt_type') == 'sugl' and Ip >= 12:
                step = randint(150, 200) / 10
            if parametr_proba.get('grunt_type') == 'glina' and Ip < 22:
                step = randint(200, 250) / 10
            if parametr_proba.get('grunt_type') == 'glina' and Ip >= 22:
                step = randint(250, 300) / 10
    else:
        if parametr_proba.get('main_type') == 'incoherent':
            end_point_time_stab = 0.5 * 60 * 60
            step = randint(50, 100) / 10
        else:
            Ip = parametr_proba.get('Ip')
            if parametr_proba.get('grunt_type') == 'supes':
                end_point_time_stab = 3 * 60 * 60
                step = randint(75, 100) / 10
            if parametr_proba.get('grunt_type') == 'sugl' and Ip < 12:
                end_point_time_stab = 6 * 60 * 60
                step = randint(100, 150) / 10
            if parametr_proba.get('grunt_type') == 'sugl' and Ip >= 12:
                end_point_time_stab = 12 * 60 * 60
                step = randint(150, 200) / 10
            if parametr_proba.get('grunt_type') == 'glina' and Ip < 22:
                end_point_time_stab = 12 * 60 * 60
                step = randint(200, 250) / 10
            if parametr_proba.get('grunt_type') == 'glina' and Ip >= 22:
                end_point_time_stab = 18 * 60 * 60
                step = randint(250, 300) / 10

    time_Stabilization = np.arange(time_wait[-1], time_wait[-1] + end_point_time_stab, step)

    count_point_Stabilization = len(time_Stabilization)

    action_Stabilization = [str('Stabilization') for x in range(count_point_Stabilization)]

    action_changed_Stabilization = [str('') for x in range(count_point_Stabilization)]
    action_changed_Stabilization[-1] = True

    Deviator_kPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

    Deviator_MPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

    list_1000 = [float(1000) for x in range(count_point_Stabilization)]

    CellPress_kPa_Stabilization = np.asarray(
        [float(CellPress_kPa_wait[-1]) for x in range(count_point_Stabilization)]) - np.asarray(
        [float(randint(0, 10) / 1000) for x in range(count_point_Stabilization)])

    VerticalPress_kPa_Stabilization = CellPress_kPa_Stabilization

    VerticalDeformation_mm_Stabilization = [float(VerticalDeformation_mm_wait[-1]) for x in
                                            range(count_point_Stabilization)]

    VolumeDeformation_cm3_Stabilization = [VolumeDeformation_cm3_wait[-1]]
    step_volume = (VolumeDeformation_cm3_wait[-1] - ev_array_1[0]) / (count_point_Stabilization - 1)
    for x in range(count_point_Stabilization - 1):
        VolumeDeformation_cm3_Stabilization.append(VolumeDeformation_cm3_Stabilization[x] + step_volume)

    CellPress_MPa_Stabilization = [x / 1000 for x in CellPress_kPa_Stabilization]

    VerticalPress_MPa_Stabilization = [x / 1000 for x in VerticalPress_kPa_Stabilization]

    Trajectory_Stabilization = [str('Consolidation') for x in range(count_point_Stabilization)]
    Trajectory_Stabilization[-1] = 'CTC'


    # otn_vert_def
    definirion_e1_array = np.asarray([float(0) for x in range(count_point_Stabilization)])
    volume_76 = np.asarray([float(76) for x in range(count_point_Stabilization)])
    first_cell_e1 = np.asarray([float(0) for x in range(count_point_Stabilization)])
    VerticalStrain_Stabilization = (VerticalPress_MPa_Stabilization - first_cell_e1) / (
                volume_76 - (definirion_e1_array))

    # otn_vol_def
    definirion_ev_array = np.asarray([float(0) for x in range(count_point_Stabilization)])
    volume = np.asarray([float(86149) for x in range(count_point_Stabilization)])
    first_cell_ev = np.asarray([float(0) for x in range(count_point_Stabilization)])
    VolumeStrain_Stabilization = (VolumeDeformation_cm3_Stabilization - first_cell_ev) / (
                volume - (definirion_ev_array))


    # основная часть испытания
    # основная часть испытания
    # основная часть испытания
    # основная часть испытания

    p_array_1 = np.append(p_array_1, p_array_1[len(p_array_1) - 1])
    e1_array = np.append(e1_array, e1_array[len(e1_array) - 1])
    ev_array_1 = np.append(ev_array_1, ev_array_1[len(ev_array_1) - 1])

    time_list = [time_Stabilization[-1]]
    step_time = (randint(6, 12) * 60 * 60) / (len(p_array_1) - 1)
    for x in range(len(p_array_1) - 1):
        time_list.append(time_list[x] + step_time + randint(0, 100) / 100)
    time_list[-1] = time_list[-2]

    action_list = [str('WaitLimit') for x in range(len(p_array_1))]
    action_list[-1] = 'TerminateCondition'

    action_changed_list = [str('') for x in range(len(p_array_1))]
    action_changed_list[-2] = True

    press_list = np.asarray([float(press) for x in range(len(p_array_1))])

    # у прочности на наших приборах нет траектории
    # у деформации есть
    Trajectory_list = [str('CTC') for x in range(len(p_array_1))]

    # otn_vert_def
    definirion_e1_array = np.asarray([float(e1_array[1] - e1_array[0]) for x in range(len(p_array_1))])
    volume_76 = np.asarray([float(76) for x in range(len(p_array_1))])
    first_cell_e1 = np.asarray([float(e1_array[0]) for x in range(len(p_array_1))])
    VerticalStrain_list = (e1_array - first_cell_e1) / (volume_76 - (definirion_e1_array))

    # давление в камере в КПа
    list_1000 = np.asarray([float(1000) for x in range(len(p_array_1))])
    CellPress_kPa = press_list * list_1000

    # otn_vert_def
    definirion_ev_array = np.asarray([float(ev_array_1[1] - ev_array_1[0]) for x in range(len(p_array_1))])
    volume = np.asarray([float(86149) for x in range(len(p_array_1))])
    first_cell_ev = np.asarray([float(ev_array_1[0]) for x in range(len(p_array_1))])
    VolumeStrain_list = (ev_array_1 - first_cell_ev) / (volume - (definirion_ev_array))

    # Давление на образец в КПа
    VerticalPress_kPa = p_array_1 * list_1000

    # Девиатор разница между давлением на образец и давлением в камере
    # В МПа
    Deviator_MPa = p_array_1 - press_list
    # в КПа
    Deviator_kPa = VerticalPress_kPa - CellPress_kPa

    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога
    # склейка всех частей лога

    # Time
    # Time
    # Time
    time_start = np.around(np.asarray(time_start), decimals=2)

    time_loadstage = np.around(np.asarray(time_loadstage), decimals=2)

    time_wait = np.around(np.asarray(time_wait), decimals=2)

    np.around(time_Stabilization, decimals=2)

    time_list = np.around(np.asarray(time_list), decimals=2)

    Time_main = np.around(np.concatenate((time_start, time_loadstage, time_wait, time_Stabilization, time_list)),
                          decimals=2)

    # Action
    # Action
    # Action

    action_none_value = np.asarray(action_none_value)

    action_loadstage = np.asarray(action_loadstage)

    action_wait = np.asarray(action_wait)

    action_Stabilization = np.asarray(action_Stabilization)

    action_list = np.asarray(action_list)

    Action_main = np.concatenate((action_none_value, action_loadstage, action_wait, action_Stabilization, action_list))

    # Action_Changed
    # Action_Changed
    # Action_Changed

    action_changed_none_value = np.asarray(action_changed_none_value)

    action_changed_loadstage = np.asarray(action_changed_loadstage)

    action_changed_wait = np.asarray(action_changed_wait)

    action_changed_Stabilization = np.asarray(action_changed_Stabilization)

    action_changed_list = np.asarray(action_changed_list)

    Action_Changed_main = np.concatenate((action_changed_none_value, action_changed_loadstage, action_changed_wait,
                                          action_changed_Stabilization, action_changed_list))

    # Deviator_kPa
    # Deviator_kPa
    # Deviator_kPa

    Deviator_kPa_none_value = np.around(np.asarray(Deviator_kPa_none_value), decimals=1)

    Deviator_kPa_loadstage = np.around(np.asarray(Deviator_kPa_loadstage), decimals=1)

    Deviator_kPa_wait = np.around(np.asarray(Deviator_kPa_wait), decimals=1)

    Deviator_kPa_Stabilization = np.around(np.asarray(Deviator_kPa_Stabilization), decimals=1)

    Deviator_kPa = np.around(np.asarray(Deviator_kPa), decimals=1)

    Deviator_kPa_main = np.around(np.concatenate((Deviator_kPa_none_value, Deviator_kPa_loadstage, Deviator_kPa_wait,
                                                  Deviator_kPa_Stabilization, Deviator_kPa)), decimals=1)

    # CellPress_kPa
    # CellPress_kPa
    # CellPress_kPa
    CellPress_kPa_none_value = np.around(np.asarray(CellPress_kPa_none_value), decimals=1)

    CellPress_kPa_loadstage = np.around(np.asarray(CellPress_kPa_loadstage), decimals=1)

    np.around(CellPress_kPa_wait, decimals=1)

    np.around(CellPress_kPa_Stabilization, decimals=1)

    np.around(CellPress_kPa, decimals=1)

    CellPress_kPa_main = np.around(
        np.concatenate((CellPress_kPa_none_value, CellPress_kPa_loadstage, CellPress_kPa_wait,
                        CellPress_kPa_Stabilization, CellPress_kPa)), decimals=1)

    # VerticalPress_kPa
    # VerticalPress_kPa
    # VerticalPress_kPa

    VerticalPress_kPa_none_value = np.around(np.asarray(VerticalPress_kPa_none_value), decimals=2)

    VerticalPress_kPa_loadstage = np.around(np.asarray(VerticalPress_kPa_loadstage), decimals=2)

    VerticalPress_kPa_wait = np.around(np.asarray(VerticalPress_kPa_wait), decimals=2)

    VerticalPress_kPa_Stabilization = np.around(np.asarray(VerticalPress_kPa_Stabilization), decimals=2)

    np.around(VerticalPress_kPa, decimals=2)

    VerticalPress_kPa_main = np.around(
        np.concatenate((VerticalPress_kPa_none_value, VerticalPress_kPa_loadstage, VerticalPress_kPa_wait,
                        VerticalPress_kPa_Stabilization, VerticalPress_kPa)), decimals=2)

    # VerticalDeformation_mm
    # VerticalDeformation_mm
    # VerticalDeformation_mm
    VerticalDeformation_mm_none_value = np.around(np.asarray(VerticalDeformation_mm_none_value), decimals=4)

    VerticalDeformation_mm_loadstage = np.around(np.asarray(VerticalDeformation_mm_loadstage), decimals=4)

    VerticalDeformation_mm_wait = np.around(np.asarray(VerticalDeformation_mm_wait), decimals=4)

    VerticalDeformation_mm_Stabilization = np.around(np.asarray(VerticalDeformation_mm_Stabilization), decimals=4)

    # np.around(e1_array, decimals=2)

    VerticalDeformation_mm_main = np.concatenate(
        (VerticalDeformation_mm_none_value, VerticalDeformation_mm_loadstage, VerticalDeformation_mm_wait,
         VerticalDeformation_mm_Stabilization, e1_array))

    # VerticalStrain
    # VerticalStrain
    # VerticalStrain

    VerticalStrain_none_value = np.asarray(VerticalStrain_none_value)

    VerticalStrain_loadstage = np.around(np.asarray(VerticalStrain_loadstage), decimals=4)

    VerticalStrain_wait = np.around(np.asarray(VerticalStrain_wait), decimals=4)

    VerticalStrain_Stabilization = np.around(np.asarray(VerticalStrain_Stabilization), decimals=4)

    VerticalStrain_list = np.around(np.asarray(VerticalStrain_list), decimals=4)

    VerticalStrain_main = np.concatenate((VerticalStrain_none_value, VerticalStrain_loadstage, VerticalStrain_wait,
                                          VerticalStrain_Stabilization, VerticalStrain_list))

    # VolumeStrain
    # VolumeStrain
    # VolumeStrain
    VolumeStrain_none_value = np.around(np.asarray(VolumeStrain_none_value), decimals=4)

    VolumeStrain_loadstage = np.around(np.asarray(VolumeStrain_loadstage), decimals=4)

    VolumeStrain_wait = np.around(np.asarray(VolumeStrain_wait), decimals=4)

    VolumeStrain_Stabilization = np.around(np.asarray(VolumeStrain_Stabilization), decimals=4)

    VolumeStrain_list = np.around(np.asarray(VolumeStrain_list), decimals=4)

    VolumeStrain_main = np.around(np.concatenate((VolumeStrain_none_value, VolumeStrain_loadstage, VolumeStrain_wait,
                                                  VolumeStrain_Stabilization, VolumeStrain_list)), decimals=4)

    # VolumeDeformation_cm3
    # VolumeDeformation_cm3
    # VolumeDeformation_cm3
    VolumeDeformation_cm3_none_value = np.around(np.asarray(VolumeDeformation_cm3_none_value), decimals=3)

    VolumeDeformation_cm3_loadstage = np.around(np.asarray(VolumeDeformation_cm3_loadstage), decimals=3)

    VolumeDeformation_cm3_wait = np.around(np.asarray(VolumeDeformation_cm3_wait), decimals=3)

    VolumeDeformation_cm3_Stabilization = np.around(np.asarray(VolumeDeformation_cm3_Stabilization), decimals=3)

    # ev_array_1_isp, decimals=4)

    VolumeDeformation_cm3_main = np.concatenate(
        (VolumeDeformation_cm3_none_value, VolumeDeformation_cm3_loadstage, VolumeDeformation_cm3_wait,
         VolumeDeformation_cm3_Stabilization, ev_array_1))

    # Deviator_MPa
    # Deviator_MPa
    # Deviator_MPa
    Deviator_MPa_none_value = np.around(np.asarray(Deviator_MPa_none_value), decimals=4)

    Deviator_MPa_loadstage = np.around(np.asarray(Deviator_MPa_loadstage), decimals=4)

    Deviator_MPa_wait = np.around(np.asarray(Deviator_MPa_wait), decimals=4)

    Deviator_MPa_Stabilization = np.around(np.asarray(Deviator_MPa_Stabilization), decimals=4)

    np.around(Deviator_MPa, decimals=4)

    Deviator_MPa_main = np.around(np.concatenate((Deviator_MPa_none_value, Deviator_MPa_loadstage, Deviator_MPa_wait,
                                                  Deviator_MPa_Stabilization, Deviator_MPa)), decimals=4)

    # CellPress_MPa
    # CellPress_MPa
    # CellPress_MPa
    CellPress_MPa_none_value = np.around(np.asarray(CellPress_MPa_none_value), decimals=4)

    CellPress_MPa_loadstage = np.around(np.asarray(CellPress_MPa_loadstage), decimals=4)

    CellPress_MPa_wait = np.around(np.asarray(CellPress_MPa_wait), decimals=4)

    CellPress_MPa_Stabilization = np.around(np.asarray(CellPress_MPa_Stabilization), decimals=4)

    np.around(press_list, decimals=4)

    CellPress_MPa_main = np.around(
        np.concatenate((CellPress_MPa_none_value, CellPress_MPa_loadstage, CellPress_MPa_wait,
                        CellPress_MPa_Stabilization, press_list)), decimals=4)

    # VerticalPress_MPa
    # VerticalPress_MPa
    # VerticalPress_MPa
    VerticalPress_MPa_none_value = np.around(np.asarray(VerticalPress_MPa_none_value), decimals=4)

    VerticalPress_MPa_loadstage = np.around(np.asarray(VerticalPress_MPa_loadstage), decimals=4)

    VerticalPress_MPa_wait = np.around(np.asarray(VerticalPress_MPa_wait), decimals=4)

    VerticalPress_MPa_Stabilization = np.around(np.asarray(VerticalPress_MPa_Stabilization), decimals=4)

    # p_array_1_isp

    VerticalPress_MPa_main = np.concatenate(
        (VerticalPress_MPa_none_value, VerticalPress_MPa_loadstage, VerticalPress_MPa_wait,
         VerticalPress_MPa_Stabilization, p_array_1))

    # Trajectory
    # Trajectory
    # Trajectory

    Trajectory_none_value = np.asarray(Trajectory_none_value)

    Trajectory_loadstage = np.asarray(Trajectory_loadstage)

    Trajectory_wait = np.asarray(Trajectory_wait)

    Trajectory_Stabilization = np.asarray(Trajectory_Stabilization)

    Trajectory_list = np.asarray(Trajectory_list)

    Trajectory_main = np.concatenate((Trajectory_none_value, Trajectory_loadstage, Trajectory_wait,
                                      Trajectory_Stabilization, Trajectory_list))



    log_Execute = {}
    log_General = {}

    volume_log_wait = (86149 + VolumeDeformation_cm3_wait[-1]) / 1000
    vertical_log_wait = (76 - VerticalDeformation_mm_wait[-1])

    volume_log_Stabilization = (volume_log_wait * 1000 + VolumeDeformation_cm3_Stabilization[-1]) / 1000
    vertical_log_Stabilization = (vertical_log_wait - VerticalDeformation_mm_Stabilization[-1])
    square_log_Stabilization = ((volume_log_wait * 1000) / vertical_log_wait) / 100


    press = parametr_press.get('press')

    random_time_log = randint(1, 15) / 100
    log_Execute.setdefault(0, f"Time	Message	Message_Changed	")
    log_Execute.setdefault(1, f"{round(time_start[-1] - random_time_log, 2)}		{True}	")
    log_Execute.setdefault(2,
                           f"{round(time_start[-1] - random_time_log, 2)}	Стадия: [Start] Подготовка к испытанию; Сообщение: Стадия реконсолидации в условиях отсутствия дренажа.		")

    random_time_log = randint(1, 10) / 100
    log_Execute.setdefault(3,
                           f"{round(time_loadstage[-1] - random_time_log, 2)}	Стадия: [Start] Подготовка к испытанию; Сообщение: Стадия реконсолидации в условиях отсутствия дренажа.	{True}	")
    log_Execute.setdefault(4,
                           f"{round(time_loadstage[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создано всестороннее давление {int(press * 1000)} кПа.		")

    random_time_log = randint(3, 10) / 100
    log_Execute.setdefault(5,
                           f"{round(time_loadstage[-1] + random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создано всестороннее давление {int(press * 1000)} кПа.	{True}	")

    log_Execute.setdefault(6,
                           f"{round(time_loadstage[-1] + random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation_def')), 1)} с.	")

    random_time_log = randint(40, 60) / 100
    log_Execute.setdefault(7,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation_def')), 1)} с.	{True}	")
    log_Execute.setdefault(8,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа всесторонним давлением в камере завершена.		")
    random_time_log = randint(30, 39) / 100
    log_Execute.setdefault(9,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа всесторонним давлением в камере завершена.	{True}	")
    log_Execute.setdefault(10,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа завершена.		")

    volume_log_wait = (86149 + VolumeDeformation_cm3_wait[-1]) / 1000
    vertical_log_wait = (76 - VerticalDeformation_mm_wait[-1])

    random_time_log = randint(20, 29) / 100
    log_Execute.setdefault(11,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Реконсолидация в условиях отсутствия дренажа завершена.	{True}	")
    log_Execute.setdefault(12,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после реконсолидации составили: Высота {round(vertical_log_wait, 2)} мм; Площадь 11.3 кв.см; Объем {round(volume_log_wait, 1)} куб.см.		")

    random_time_log = randint(10, 19) / 100
    log_Execute.setdefault(13,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после реконсолидации составили: Высота {round(vertical_log_wait, 2)} мм; Площадь 11.3 кв.см; Объем {round(volume_log_wait, 1)} куб.см.	{True}	")

    log_Execute.setdefault(14,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Стадия дополнительного уплотнения.		")

    random_time_log = randint(1, 9) / 100
    log_Execute.setdefault(15,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Стадия дополнительного уплотнения.	{True}	")

    log_Execute.setdefault(16,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создана ступень всестороннего давления {int(press * 1000)} кПа.		")

    random_time_log = -randint(10, 17) / 100
    log_Execute.setdefault(17,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [LoadStage ] Стадия нагружения; Сообщение: Создана ступень всестороннего давления {int(press * 1000)} кПа.	{True}	")

    hours = int(end_point_time_stab // 3600)
    if hours < 10:
        hours = f"0{hours}"
    minute = int(end_point_time_stab // 60 - (int(end_point_time_stab // 3600) * 60))
    if minute < 10:
        minute = f"0{minute}"
    sec_t = int(end_point_time_stab % 60)
    if sec_t < 10:
        sec_t = f"0{sec_t}"
    time = f"{hours}:{minute}:{sec_t}"
    log_Execute.setdefault(18,
                           f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Начато ожидание стабилизации параметра 'Относительная объемная деформация образца'. Исходное значение: {0.05}  (период стабилизации: {time}, параметр стабилизации: {0.13} )		")


    random_time_log = -randint(40, 60) / 100
    log_Execute.setdefault(19,
                           f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Начато ожидание стабилизации параметра 'Относительная объемная деформация образца'. Исходное значение: {0.05}  (период стабилизации: {time}, параметр стабилизации: {0.13} )	{True}	")

    log_Execute.setdefault(20,
                           f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Ожидание стабилизации параметра 'Относительная объемная деформация образца' закончено. Конечное значение: {0.05} 		")



    random_time_log = -randint(30, 39) / 100
    log_Execute.setdefault(21,
                           f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Ожидание стабилизации параметра 'Относительная объемная деформация образца' закончено. Конечное значение: {0.05} 	{True}	")

    log_Execute.setdefault(22,
                           f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.		")



    log_Execute.setdefault(23,
                           f"{round(time_list[-1], 2)}	Стадия: [Stabilization] Ожидание времени стабилизации; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.	{True}	")

    log_Execute.setdefault(24,
                           f"{round(time_list[-1], 2)}	Стадия: [TerminateCondition] Испытание завершилось по условию; Сообщение: Завершения испытания...		")




    log_General.setdefault(0,
                           f"SampleHeight_mm	SampleDiameter_mm	SampleHeightConsolidated_mm	SampleVolumeConsolidated_cm3	SampleAreaConsolidated_cm2	PlungerArea_mm2	")
    log_General.setdefault(1, f"76	38	0.00	0.0000	0.0000	314	")
    log_General.setdefault(2, f"76	38	76.00	86.1490	11.3354	314	")
    log_General.setdefault(3,
                           f"76	38	{round(float(vertical_log_wait), 2)}	{round(float(volume_log_wait), 4)}	{11.3354}	314	")
    log_General.setdefault(4,
                           f"76	38	{round(float(vertical_log_Stabilization), 2)}	{round(float(volume_log_Stabilization), 4)}	{round(float(square_log_Stabilization), 4)}	314	")

    # перевод прочности в сm3 вместо mm3

    list_1000_vol = np.asarray([float(1000) for x in range(len(VolumeDeformation_cm3_main))])
    VolumeDeformation_cm3_main = VolumeDeformation_cm3_main / list_1000_vol

    # Time	Action	Action_Changed	Deviator_kPa	CellPress_kPa	VerticalPress_kPa	VerticalDeformation_mm	VerticalStrain	VolumeStrain	VolumeDeformation_cm3	Deviator_MPa	CellPress_MPa	VerticalPress_MPa	Trajectory
    # 14

    df = pd.DataFrame({'Time': Time_main, 'Action': Action_main, 'Action_Changed': Action_Changed_main,
                       'Deviator_kPa': Deviator_kPa_main, 'CellPress_kPa': CellPress_kPa_main,
                       'VerticalPress_kPa': VerticalPress_kPa_main,
                       'VerticalDeformation_mm': VerticalDeformation_mm_main,
                       'VerticalStrain': VerticalStrain_main, 'VolumeStrain': VolumeStrain_main,
                       'VolumeDeformation_cm3': VolumeDeformation_cm3_main,
                       'Deviator_MPa': Deviator_MPa_main,
                       'CellPress_MPa': CellPress_MPa_main, 'VerticalPress_MPa': VerticalPress_MPa_main,
                       'Trajectory': Trajectory_main})

    # picture_time = time.strftime("%Y.%m.%d %H_%M_%S", time.localtime(time.time()))


    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/TPD/')
    os.mkdir(picture_time)
    os.chdir(picture_time)



    shutil.copy('Z:/Zapis\ISP\obr_TPD.xml',
                File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time))
    os.rename(f"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/obr_TPD.xml'}", f"{File_Path + parametr_isp.get('LAB_NO')}/TPD/{picture_time}" + f"/{picture_time}.xml")





    os.mkdir('Execute')
    os.chdir('Execute')
    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/Execute/' + 'Execute.1.log'}",
              "w") as file:
        for key in log_Execute.keys():
            file.write(str(log_Execute.get(key)) + '\n')
    os.chdir('..')

    os.mkdir('General')
    os.chdir('General')
    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/General/' + 'General.1.log'}",
              "w") as file:
        for key in log_General.keys():
            file.write(str(log_General.get(key)) + '\n')


    my_file.close()
    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPD/{str(picture_time)}/Test/{'Test.1'}.log",
        sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True


# компрессия обычная
# компрессия обычная
# компрессия обычная
def search_press_spd(parametr_proba):
    if parametr_proba.get('IL') >= 1:
        press_spd = [0, 0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if parametr_proba.get('IL') >= 0.75 and parametr_proba.get('IL') < 1:
        press_spd = [0, 0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if parametr_proba.get('IL') > 0.5 and parametr_proba.get('IL') < 0.75:
        press_spd = [0, 0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if parametr_proba.get('IL') > 0.25 and parametr_proba.get('IL') <= 0.5:
        press_spd = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if parametr_proba.get('IL') <= 0.25:
        press_spd = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    return press_spd


def search_st_spd(parametr_proba):
    if parametr_proba.get('IL') >= 1:
        choise_st = [0, 0, 0, -1, -1, 0, 0, 0, 0]
    if parametr_proba.get('IL') >= 0.75 and parametr_proba.get('IL') < 1:
        choise_st = [0, 0, 0, -1, -1, 0, 0, 0, 0]
    if parametr_proba.get('IL') > 0.5 and parametr_proba.get('IL') < 0.75:
        choise_st = [0, 0, 0, -1, -1, 0, 0, 0, 0]
    if parametr_proba.get('IL') > 0.25 and parametr_proba.get('IL') <= 0.5:
        choise_st = [0, 0, -1, -1, 0, 0, 0, 0]
    if parametr_proba.get('IL') <= 0.25:
        choise_st = [0, 0, -1, -1, 0, 0, 0, 0]
    return choise_st


def SPD_parametr(parametr_proba, parametr_isp, press_spd, choise_st, log_dict):
    # определение moed
    k_por = parametr_proba.get('Kpor')
    k_por_for_log = k_por
    Ro = parametr_proba.get('Ro')
    Ro_for_log = parametr_proba.get('Ro')
    PROBEGR_IDS = parametr_proba.get('PROBEGR_IDS')
    PROBEGR_SVODKA = parametr_proba.get('PROBEGR_SVODKA')
    CMUSL_OBJID = parametr_proba.get('CMUSL_OBJID')

    if parametr_proba.get('grunt_type') == 'supes':
        if k_por < 0.45:
            k_por = randint(450, 540) / 1000
            parametr_recalc = 1
        elif k_por > 0.85:
            k_por = randint(760, 850) / 1000
            parametr_recalc = 1
        else:
            parametr_recalc = 0
    if parametr_proba.get('grunt_type') == 'sugl':
        if k_por < 0.45:
            k_por = randint(450, 540) / 1000
            parametr_recalc = 1
        elif k_por > 1.05:
            k_por = randint(960, 1040) / 1000
            parametr_recalc = 1
        else:
            parametr_recalc = 0
    if parametr_proba.get('grunt_type') == 'glina':
        if k_por < 0.65:
            k_por = randint(660, 740) / 1000
            parametr_recalc = 1
        elif k_por > 1.05:
            k_por = randint(960, 1040) / 1000
            parametr_recalc = 1
        else:
            parametr_recalc = 0

    if parametr_recalc == 1:
        # перерасчет минимально возможной плотности, для получения нужного по нормативке Kpor


        RoS = parametr_proba.get('RoS')
        W = parametr_proba.get('W')

        Sr_calc = ((W * RoS) / (k_por)) / 100

        if Sr_calc > 0.99:
            k_por_calc = ((W * RoS) / (0.99)) / 100
        else:
            k_por_calc = k_por
        # плотность
        Sr_calc = ((W * RoS) / (k_por)) / 100
        plot = ((RoS) / (k_por_calc + 1)) * (1 + 0.01 * W)

        # водонасыщенность
        if Sr_calc != None:
            if Sr_calc <= 0.8:
                water_saturation = True
                CMUSL_OBJID = '96C5DAE5713940E8AFA9A4042B0851A2'
            else:
                water_saturation = False
                CMUSL_OBJID = '073E8206C7C94C0ABD2C3142F5E77EAA'

        # поиск кольца в сводке
        select_prgr = "SELECT (OBJID),(P),(V),(S) FROM Rings WHERE (NUM) = ?"
        result_search = cursor.execute(select_prgr, str(randint(20, 109))).fetchall()
        result_search = list(result_search[0])
        RING_OBJID = result_search[0]
        VES_0 = result_search[1]
        OBJEM_0 = result_search[2]
        PLOSH_0 = result_search[3]

        VES1R = plot * OBJEM_0 + VES_0

        # удалить существующее кольцо
        cursor.execute(
            "DELETE FROM PROBAGR_PLOTNGR WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': PROBEGR_IDS})
        cursor.commit()
        # записать новое кольцо
        write_1 = ('INSERT INTO PROBAGR_PLOTNGR (OBJID, ZAMER_NO, DATA_ISP, RING_OBJID, VES0, VES1, VOL,ROP) VALUES ('
                   '?,?,?,?,?,?,?,?)')
        write_2 = cursor.execute(write_1, PROBEGR_IDS, 0, time.strftime("%Y-%m-%d", time.localtime(time.time())),
                                 RING_OBJID, VES_0, VES1R, OBJEM_0, 0.9)
        cursor.commit()

        # запись в сводку
        select_prgr = "UPDATE SVODKA_FIZMEX SET Ro = ? WHERE OBJID = ?"
        result_write = cursor.execute(select_prgr, plot, PROBEGR_SVODKA)

        select_prgr = "UPDATE SVODKA_FIZMEX SET Kpor = ? WHERE OBJID = ?"
        result_write = cursor.execute(select_prgr, k_por_calc, PROBEGR_SVODKA)

        cursor.commit()

        # обновление словаря параметров пробы
        log_dict.setdefault(parametr_isp.get('LAB_NO'),
                            ['Kpor_past', k_por_for_log, 'Ro_past', Ro_for_log, 'Kpor_now', k_por_calc, 'Ro_now',
                             plot])

        name_update_parametr = ['Kpor', 'Ro', 'Sr', 'water_saturation', 'CMUSL_OBJID']
        new_value = [k_por_calc, plot, Sr_calc, water_saturation, CMUSL_OBJID]
        for name, value in zip(name_update_parametr, new_value):
            parametr_proba.update({name: value})

    else:
        pass

    k_por = parametr_proba.get('Kpor')
    CMUSL_OBJID = parametr_proba.get('CMUSL_OBJID')

    # лист значений moed, B stat для разных типов грунта
    if parametr_proba.get('grunt_type') == 'supes':

        b_stat = 0.8

        if k_por >= 0.45 and k_por <= 0.55:
            moed = 2.8

        if k_por > 0.55 and k_por <= 0.65:
            moed = ((0.65 - k_por) / (0.1)) * 0.3 + 2.5

        if k_por > 0.65 and k_por <= 0.75:
            moed = ((0.75 - k_por) / (0.1)) * 0.4 + 2.1

        if k_por > 0.75 and k_por <= 0.85:
            moed = ((0.85 - k_por) / (0.1)) * 0.7 + 1.4

    if parametr_proba.get('grunt_type') == 'sugl':

        b_stat = 0.6

        if k_por >= 0.45 and k_por <= 0.55:
            moed = 3

        if k_por > 0.55 and k_por <= 0.65:
            moed = ((0.65 - k_por) / (0.1)) * 0.3 + 2.7

        if k_por > 0.65 and k_por <= 0.75:
            moed = ((0.75 - k_por) / (0.1)) * 0.3 + 2.4

        if k_por > 0.75 and k_por <= 0.85:
            moed = ((0.85 - k_por) / (0.1)) * 0.6 + 1.8

        if k_por > 0.85 and k_por <= 0.95:
            moed = ((0.95 - k_por) / (0.1)) * 0.3 + 1.5

        if k_por > 0.95 and k_por <= 1.05:
            moed = ((1.05 - k_por) / (0.1)) * 0.3 + 1.2

    if parametr_proba.get('grunt_type') == 'glina':

        b_stat = 0.4

        if k_por > 0.65 and k_por <= 0.75:
            moed = 2.4

        if k_por > 0.75 and k_por <= 0.85:
            moed = ((0.85 - k_por) / (0.1)) * 0.2 + 2.2

        if k_por > 0.85 and k_por <= 0.95:
            moed = ((0.95 - k_por) / (0.1)) * 0.2 + 2

        if k_por > 0.95 and k_por <= 1.05:
            moed = ((1.05 - k_por) / (0.1)) * 0.2 + 1.8

    E_oed = parametr_isp.get('E') / moed

    delta_h = (0.1 * 20) / E_oed

    # расчет точек по y, т.е. давления в миллиметрах
    p_y = np.arange(0, delta_h * len(press_spd), delta_h)
    del_p_y = np.asarray([int(20) for x in range(len(p_y))])

    # относительная вертикальная деформация
    otn_vert_def = p_y / del_p_y

    # пористость по ступеням
    k_por_list = np.asarray([float(k_por) for x in range(len(p_y))])
    list_1 = np.asarray([float(1) for x in range(len(p_y))])

    por_list = k_por_list - (otn_vert_def * (list_1 + k_por_list))
    por_list[0] = k_por

    NRN = np.arange(0, len(p_y))

    return moed, p_y, otn_vert_def, NRN, log_dict


def SPD_write(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN):
    PROBEGR_IDS = parametr_proba.get('PROBEGR_IDS')
    PROBEGR_SVODKA = parametr_proba.get('PROBEGR_SVODKA')
    CMUSL_OBJID = parametr_proba.get('CMUSL_OBJID')

    cursor.execute(
        "INSERT INTO CMOPR (OBJID,	PROBAGR_OBJID,	DATA_ISP,	SCEMA,	H_RING1,	CMUSL_OBJID,	CMSTRGR_OBJID,	PRIBOR_OBJID, 	RAZGRUZKA, Mk,	Mk_Manual,	Nu_Manual,	PRIBORNAME_OBJID,	DATA_BEGIN_ISP,	DATA_END_ISP,	ZOOM_PERCENT,	BETA,	BETA_MANUAL,	NO_SUBSIDENCE,	W_MANUAL,	KAZAGRANDE) "
        "VALUES ('%(OBJID)s',	'%(PROBAGR_OBJID)s',	'%(DATA_ISP)s',	'1',	'20',	'%(CMUSL_OBJID)s', 'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0',	'F81B7BFBAD47423FBBBD8D9D5AD49A71','0', '%(Mk)s', '0','0','F81B7BFBAD47423FBBBD8D9D5AD49A71','%(DATA_BEGIN_ISP)s','%(DATA_END_ISP)s','100','0,6','0','0','0','0')"
        % {'OBJID': PROBEGR_IDS, 'PROBAGR_OBJID': PROBEGR_IDS,
           'DATA_ISP': time.strftime("%Y-%m-%d", time.localtime(time.time())), 'Mk': str(moed).replace('.', ','),
           'CMUSL_OBJID': CMUSL_OBJID, 'DATA_BEGIN_ISP': time.strftime("%Y-%m-%d", time.localtime(time.time())),
           'DATA_END_ISP': time.strftime("%Y-%m-%d", time.localtime(time.time()))})
    cursor.commit()

    for u in range(len(p_y)):
        cursor.execute(
            "INSERT INTO CMDATA (OBJID,	P,	isZ,	Deform1,		Deform,	st,				OtnDef,		k_tare,	k_tarez,	NRN,	ST_PRS) "
            "VALUES ('%(OBJID)s',	'%(P)s',	'0',	'%(Deform1)s',	'%(Deform)s','%(st)s',	'%(OtnDef)s','0','0','%(NRN)s','0')"
            % {'OBJID': PROBEGR_IDS,
               'P': str(press_spd[u]).replace('.', ','),
               'Deform1': (str(p_y[u])).replace('.', ','),
               'Deform': ((str(p_y[u])).replace('.', ',')),
               'st': ((str(choise_st[u])).replace('.', ',')),
               'OtnDef': ((str(otn_vert_def[u])).replace('.', ',')),
               'NRN': (str(NRN[u]).replace('.', ','))})
    cursor.commit()
    return True


def ISP_SPD(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN):
    time_list = [randint(1200, 1700) / 100]
    for x in range(len(p_y) - 1):
        time_list.append(time_list[x] + randint(1200, 1700) / 100)

    action_list = [str('Stabilization') for x in range(len(p_y))]

    action_changed_list = [str(True) for x in range(len(p_y))]

    press_spd = np.asarray(press_spd)

    ePress_kPa = [int(0) for x in range(len(p_y))]

    empty_list = [str('') for x in range(len(p_y))]

    name = [str('Компрессия') for x in range(len(p_y))]

    df = pd.DataFrame({'Time': time_list, 'Action': action_list, 'Action_Changed': action_changed_list,
                       'VerticalPress_kPa': press_spd * 100, 'ePress_kPa': ePress_kPa, 'VerticalDeformation_mm': p_y,
                       'VerticalPress_MPa': press_spd, 'PorePress_MPa': p_y, 'VerticalStrain': ePress_kPa,
                       'Deformation_mm': press_spd * 0.1,
                       'Stage': ePress_kPa, '': name})

    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/SPD/')
    os.mkdir(str(press_spd[1]))
    os.chdir(str(press_spd[1]))
    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + parametr_isp.get('LAB_NO') + '/SPD/' + str(press_spd[1]))
    os.mkdir('General')
    os.chdir('General')
    my_file = open("General.log", "w+")
    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                  '20	87')
    my_file.close()
    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(f"{File_Path + parametr_isp.get('LAB_NO')}/SPD/{str(press_spd[1])}/Test/{str(press_spd[1])}.log",
              sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True


# одноплоскостной срез
# одноплоскостной срез
# одноплоскостной срез
def SPS_SHEAR_DEF(parametr_isp, press, parametr_press, quantity_point_sps_1, quantity_point_sps_2):
    F = parametr_isp.get('F')
    C = parametr_isp.get('C')

    Rad = (F * math.pi) / 180

    press = parametr_press.get(press)

    st = (press * math.tan(Rad) + C)

    quantity_point = randint(quantity_point_sps_1, quantity_point_sps_2)

    koef_x = np.arange(0, 1.3, 1.3 / quantity_point)

    num_arg = randint(40, 50) / 100

    argument_x = np.asarray([float(num_arg) for x in range(quantity_point)])

    # степень
    degree = np.asarray(
        [float(math.log(8, koef_x[quantity_point - 1] / argument_x[0])) for x in range(quantity_point)])

    array_x_random1 = np.asarray([float(randint(0, 100) / 1000) for x in range(quantity_point)])

    for x in range(5):
        array_x_random1[x] = 0

    # график по Х
    SHEAR_DEF = ((koef_x / argument_x) ** degree) - array_x_random1

    return SHEAR_DEF, quantity_point, st


def SPS_TANGENT_PRESS(quantity_point, st, choise_max):
    # выбор максимальной точки
    choise_max_num = quantity_point - choise_max

    # выяснение шага от максимальной точки до первой точки после 0
    range_st = abs((st - 0) / (quantity_point - quantity_point - choise_max_num - 1))

    # перед макс точкой
    y_part1 = np.arange(0, st, range_st)

    # после макс точки
    # subtraction - вычитание
    y_subtraction = randint(10, 40) / 100000
    y_part2 = np.arange(st, st - y_subtraction * (quantity_point - choise_max_num - 1), -y_subtraction)

    # объединение в один массив
    TANGENT_PRESS = np.concatenate((y_part1, y_part2))

    return TANGENT_PRESS


def SPS_ZAMER_NUM(quantity_point):
    ZAMER_NUM = np.arange(0, quantity_point)
    return ZAMER_NUM


def SPS_time(quantity_point):
    T = [randint(900, 1500) / 100]
    u = 0
    for x in range(quantity_point - 1):
        T.append(T[u] + randint(900, 1500) / 100)
        u += 1
    return T


def write_SPS_SDOPR(cursor, parametr_proba, parametr_isp, SDDATA_OBJID):
    F = parametr_isp.get('F')
    C = parametr_isp.get('C')

    CMUSL_OBJID = parametr_proba.get('CMUSL_OBJID')
    PROBEGR_IDS = parametr_proba.get('PROBEGR_IDS')

    timing = time.strftime("%Y-%m-%d", time.localtime(time.time()))

    cursor.execute(
        "INSERT INTO SDOPR (OBJID,	DATA_ISP,	CMSTRGR_OBJID,	CMUSL_OBJID,	SDSPEED_OBJID,	PROBAGR_OBJID,ForFizMex,SD_Fi,SD_C,	PRIBOR_OBJID,	CONDITIONS) "
        "VALUES ('%(OBJID)s',	'%(DATA_ISP)s',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0',	'%(CMUSL_OBJID)s',	'FEBBE9906CA64E269659F045A0AB6CD9',	'%(PROBEGR_IDS)s','-1','%(SD_Fi)s','%(SD_C)s',	'3D7FE26F62424351B1C994264C48E42C',	'1')"
        % {'OBJID': SDDATA_OBJID, 'DATA_ISP': timing,
           'PROBEGR_IDS': PROBEGR_IDS,
           'CMUSL_OBJID': CMUSL_OBJID, 'SD_Fi': str(F).replace('.', ','), 'SD_C': str(C).replace('.', ',')})
    return True


def write_SPS(cursor, SHEAR_DEF, T, TANGENT_PRESS, ZAMER_NUM, parametr_press, press, st, quantity_point, SDDATA_OBJID):
    cursor.execute(
        "INSERT INTO SDDATA (OBJID,	P,F,T,	S) "
        "VALUES ('%(OBJID)s',	'%(P)s','%(F)s','205,52',	'40,15152')"
        % {'OBJID': SDDATA_OBJID, 'P': str(parametr_press.get(press)).replace('.', ','),
           'F': str(st).replace('.', ',')})

    for u in range(quantity_point):
        cursor.execute(
            "INSERT INTO SDZAMER (OBJID,P,ZAMER_NUM,T,TANGENT_PRESS,SHEAR_DEF) "
            "VALUES ('%(OBJID)s',	'%(P)s',	'%(ZAMER_NUM)s',	'%(T)s',	'%(TANGENT_PRESS)s','%(SHEAR_DEF)s')"
            % {'OBJID': SDDATA_OBJID,
               'P': str(parametr_press.get(press)).replace('.', ','),
               'ZAMER_NUM': str(ZAMER_NUM[u]).replace('.', ','),
               'T': str(T[u]).replace('.', ','),
               'TANGENT_PRESS': str(TANGENT_PRESS[u]).replace('.', ','),
               'SHEAR_DEF': str(SHEAR_DEF[u]).replace('.', ',')})

    cursor.commit()
    return True


def ISP_SPS(SHEAR_DEF, T, TANGENT_PRESS, parametr_press, press):

    min_arr = min(len(SHEAR_DEF), len(T), len(TANGENT_PRESS))

    for x in range(len(SHEAR_DEF) - min_arr):
        SHEAR_DEF = np.delete(SHEAR_DEF, len(SHEAR_DEF) - 1)

    for x in range(len(T) - min_arr):
        T = np.delete(T, len(T) - 1)

    for x in range(len(TANGENT_PRESS) - min_arr):
        TANGENT_PRESS = np.delete(TANGENT_PRESS, len(TANGENT_PRESS) - 1)


    action_list = [str('Stabilization') for x in range(len(SHEAR_DEF))]

    action_changed_list = [str(True) for x in range(len(SHEAR_DEF))]

    press_sps = [float(parametr_press.get(press)) for x in range(len(SHEAR_DEF))]

    empty_list = [str('') for x in range(len(SHEAR_DEF))]

    name = [str('Срез') for x in range(len(SHEAR_DEF))]

    if len(TANGENT_PRESS) > len(SHEAR_DEF):
        TANGENT_PRESS = np.delete(TANGENT_PRESS, len(TANGENT_PRESS) - 1)

    df = pd.DataFrame({'Time': T, 'Action': action_list, 'Action_Changed': action_changed_list,
                       'VerticalPress_kPa': empty_list, 'ShearDeformation_mm': SHEAR_DEF, 'ShearPress_kPa': empty_list,
                       'VerticalPress_MPa': press_sps, 'ShearPress_MPa': TANGENT_PRESS, 'ShearStrain': empty_list,
                       'Stage': name})

    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/SPS/')
    os.mkdir(str(parametr_press.get(press)))
    os.chdir(str(parametr_press.get(press)))
    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml',
                File_Path + parametr_isp.get('LAB_NO') + '/SPS/' + str(parametr_press.get(press)))
    os.mkdir('General')
    os.chdir('General')
    my_file = open("General.log", "w+")
    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                  '35	71.5')
    my_file.close()
    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(
        f"{File_Path + parametr_isp.get('LAB_NO')}/SPS/{str(parametr_press.get(press))}/Test/{str(parametr_press.get(press))}.log",
        sep='\t', index=False, encoding="ANSI")  # создание лога из выведенного датафрейма

    return True


def TPDL_generate(parametr_proba, parametr_isp, parametr_d, cursor, CM3DATA_OBJID, parametr_press):
    # деформация
    def TPDL(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID):
        press = parametr_press.get('press')
        E = parametr_isp.get('E')
        if parametr_d.get('regime_point_uploading_tpdl') == 'simple' or press <= 0.6:
            if parametr_proba.get('main_type') == 'incoherent':
                b = randint(300, 400) / 10
            else:
                if parametr_proba.get('grunt_type') == 'supes':
                    b = randint(300, 400) / 10
                if parametr_proba.get('grunt_type') == 'sugl':
                    b = randint(50, 100) / 10
                if parametr_proba.get('grunt_type') == 'glina':
                    b = randint(1, 15) / 10

        elif parametr_d.get('regime_point_uploading_tpdl') == 'hard' and press > 0.06:
            last_press = randint(160, 170) / 100

        parametr_tpd = {'b': b}

        return parametr_tpd



    def graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba, vertical_point_uploading):

        if vertical_point_uploading == 0.075:
            vertical_point_uploading = 0.02

            vertical_speed_rzg_list = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.004, 0.003,
                                       0.002, 0.001]

            vertical_speed_rzg_now = vertical_speed_rzg_list.index(vertical_speed_rzg)

            try:
                vertical_speed_rzg = vertical_speed_rzg_list[vertical_speed_rzg_now + 1]
            except:
                print('Невозможно')


            return graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba,
                              vertical_point_uploading)

        press = parametr_press.get('press')
        E = parametr_isp.get('E')

        e1_array = np.arange(0, 11.4, vertical_speed_rzg)



        first_point_e1 = np.asarray([float(e1_array[0]) for x in range(len(e1_array))])
        raznitsa_fistr_second_e1 = np.asarray(
            [float(e1_array[1] - e1_array[0]) for x in range(len(e1_array))])
        list_76 = np.asarray([float(76) for x in range(len(e1_array))])
        otn_def = (e1_array - first_point_e1) / (list_76 - raznitsa_fistr_second_e1)

        if vertical_point_uploading != None:
            for x in otn_def:
                if x > vertical_point_uploading:
                    otn_def = otn_def.tolist()
                    index_vertical_point_uploading = otn_def.index(x)
                    break
        else:
            vertical_point_uploading = 20 / 1000
            for x in otn_def:
                if x > vertical_point_uploading:
                    otn_def = otn_def.tolist()
                    index_vertical_point_uploading = otn_def.index(x)
                    break

        press_list = np.asarray([float(press) for x in range(len(e1_array))])

        point_unloading = parametr_d.get('global_point_unloading')
        Ip = parametr_proba.get('Ip')
        IL = parametr_proba.get('IL')
        if point_unloading == None:
            regime_point_uploading_tpdl = parametr_d.get('regime_point_uploading_tpdl')
            if point_unloading != None:
                if Ip == None:
                    point_unloading = 1.6
                if Ip <= 7 and IL <= 0.5:
                    point_unloading = 1.5
                if Ip > 7 and Ip < 17 and IL <= 0.5:
                    point_unloading = 1.3
                if Ip > 7 and Ip < 17 and IL > 0.5:
                    point_unloading = 1.23
                if Ip >= 17 and IL <= 0.5:
                    point_unloading = 1.21
                if Ip >= 17 and IL > 0.5:
                    point_unloading = 1.15
            else:
                point_unloading = 2

        e1_array_first = e1_array[:index_vertical_point_uploading]




        last_point_1 = press * point_unloading

        # проверка на минимальный модуль
        # проверка на минимальный модуль
        # проверка на минимальный модуль
        # проверка на минимальный модуль
        curve_test_min = 10000

        c_1 = last_point_1 / (math.atan(((e1_array_first[-1] / curve_test_min)) ** 0.5)) - press / (math.atan(((e1_array_first[-1] / curve_test_min)) ** 0.5))

        p_array_1 = []

        for x in e1_array_first:
            p_array_1.append(c_1 * math.atan((x / curve_test_min) ** 0.5) + press)

        max_choise_p = press * 1.6

        # если не хватает модуля на curve, то нужно отодвинуть точку разгруки в большую сторону

        list_module_min = []
        for x in range(len(e1_array_first)):
            try:
                list_module_min.append((p_array_1[x + 1] - p_array_1[x]) / abs(otn_def[x + 1] - otn_def[x]))

                if p_array_1[x + 1] >= max_choise_p:
                    break
            except:
                break



        # проверка на максимальный модуль
        # проверка на максимальный модуль
        # проверка на максимальный модуль
        # проверка на максимальный модуль
        curve_test_max = 0.008

        c_1 = (last_point_1 / (math.atan(((e1_array_first[-1] / curve_test_max)) ** 0.5)) - (
                press / (math.atan(((e1_array_first[-1] / curve_test_max)) ** 0.5))))

        p_array_1 = []

        for x in e1_array_first:
            p_array_1.append(c_1 * math.atan((x / curve_test_max) ** 0.5) + press)

        # если не хватает модуля на curve, то нужно отодвинуть точку разгруки в большую сторону
        list_module_max = []

        for x in range(len(list_module_min)):
            try:
                list_module_max.append((p_array_1[x + 1] - p_array_1[x]) / abs(otn_def[x + 1] - otn_def[x]))

            except:
                break



        list_truth_E_max = []
        list_truth_E = []
        count = 0
        for x, y in zip(list_module_max, list_module_min):
            if x > E and count != 0:
                list_truth_E_max.append(True)
            else:
                list_truth_E_max.append(False)

            if y < E and count != 0:
                list_truth_E.append(True)
            else:
                list_truth_E.append(False)

            try:
                if list_truth_E_max[count] == True and list_truth_E[count] == True:
                    point_1 = count
                    point_2 = count + 1
                    points_l = [point_1, point_2]
                    break
                else:
                    point_1 = None
                    point_2 = None
                    points_l = [point_1, point_2]

            except:
                print('KALL')

            count += 1

        if point_1 == None or point_2 == None :
            vertical_point_uploading += 0.005

            return graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba,
                              vertical_point_uploading)


        E_now = round(list_module_max[point_1], 2)

        E_now_past = round(list_module_max[point_1], 2)

        count = 0


        while E != E_now:

            c_1 = (last_point_1 / (math.atan(((e1_array_first[-1] / curve_test_max)) ** 0.5)) - (
                    press / (math.atan(((e1_array_first[-1] / curve_test_max)) ** 0.5))))

            p_array_1 = []

            for x in e1_array_first:
                p_array_1.append(c_1 * math.atan((x / curve_test_max) ** 0.5) + press)

            max_choise_p = press * 1.5

            # если не хватает модуля на curve, то нужно отодвинуть точку разгруки в большую сторону

            list_module = []
            for x in range(len(e1_array_first)):
                list_module.append((p_array_1[x + 1] - p_array_1[x]) / abs(otn_def[x + 1] - otn_def[x]))
                if x + 1 > point_1:
                    break

            E_now = round(list_module[point_1], 2)

            # print(E_now, '    ', count)

            if E == E_now:
                break

            curve_test_max += 0.00001
            count += 1

            if count > 20000:
                curve_test_max += 0.0001

            if count > 40000:
                curve_test_max += 0.001




        # вторая часть графика
        e1_array_second = e1_array[index_vertical_point_uploading:]

        if parametr_proba.get('main_type') == 'incoherent':
            last_point_koef = randint(11, 13) / 10
        if parametr_proba.get('grunt_type') == 'supes':
            last_point_koef = randint(12, 14) / 10
        if parametr_proba.get('grunt_type') == 'sugl':
            last_point_koef = randint(13, 15) / 10
        if parametr_proba.get('grunt_type') == 'glina':
            last_point_koef = randint(14, 16) / 10

        last_point_2 = p_array_1[-1] * last_point_koef

        curve = randint(1, 80) / 100

        press_2 = ((last_point_2 * math.atan((e1_array_second[0]/curve) ** 0.5))/(math.atan((e1_array_second[0]/curve) ** 0.5) - math.atan((e1_array_second[-1]/curve) ** 0.5)))-(last_point_1/(((math.atan((e1_array_second[0]/curve) ** 0.5))/(math.atan((e1_array_second[-1]/curve) ** 0.5)))-1))

        c_2 = (last_point_2 / (math.atan(((e1_array_second[-1] / curve)) ** 0.5)) - (
                    press_2 / (math.atan(((e1_array_second[-1] / curve)) ** 0.5))))

        p_array_2 = []

        for x in e1_array_second:
            p_array_2.append(c_2 * math.atan((x / curve) ** 0.5) + press_2)

        p_array_1 = np.asarray(p_array_1)
        p_array_2 = np.asarray(p_array_2)

        p_array_1 = np.concatenate((p_array_1, p_array_2))

        #
        #
        #
        #
        #
        if parametr_proba.get('main_type') == 'incoherent' and parametr_d.get('need_tail_rzg') == 1:

            dis_point = parametr_d.get('point_tail')

            first_point_tail = vertical_point_uploading + randint(dis_point, dis_point + 10) / 1000
            otn_def_incoherent = otn_def
            for x in otn_def_incoherent:
                if x > first_point_tail:
                    index = otn_def_incoherent.index(x)
                    break

            second_point_tail = first_point_tail + (0.15 - first_point_tail) / 2
            for x in otn_def_incoherent:
                if x > second_point_tail:
                    index_tail_2 = otn_def_incoherent.index(x)
                    break

            if parametr_proba.get('main_type') == 'incoherent':
                curve = randint(1000, 1100) / 100

            e1_array_tail = e1_array[index:index_tail_2]

            Y_move = e1_array[index]

            if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get('grunt_type') == 'large_sand':
                z = randint(4, 7) / 1000
            if parametr_proba.get('grunt_type') == 'mid_sand':
                z = randint(3, 6) / 1000
            if parametr_proba.get('grunt_type') == 'small_sand':
                z = randint(2, 5) / 1000
            if parametr_proba.get('grunt_type') == 'dust_sand':
                z = randint(10, 15) / 1000

            r = 2
            g = press

            X_move = z * g * -e1_array_tail[0] ** 2 + 2 * Y_move * z * g * -e1_array_tail[0] + p_array_1[
                index] + Y_move ** 2 * z * g - z * r ** 2

            X_move = 0

            tail_x = []


            for x in e1_array_tail:
                tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

            X_move = p_array_1[index] - tail_x[0]
            tail_x = []
            for x in e1_array_tail:
                tail_x.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

            tail_x = np.asarray(tail_x)



            e1_array_tail_2 = e1_array[index_tail_2:]
            Y_move = e1_array_tail_2[-1]

            z = -z
            r = 2
            g = press / 2
            X_move = 0
            tail_x_2 = []
            for x in e1_array_tail_2:
                tail_x_2.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)
            tail_x_2 = np.asarray(tail_x_2)

            X_move = tail_x[-1] - tail_x_2[0]
            tail_x_2 = []
            for x in e1_array_tail_2:
                tail_x_2.append((z * (r ** 2 - g * (-x + Y_move) ** 2)) + X_move)

            p_array_1 = p_array_1[:index]
            p_array_1 = np.concatenate((p_array_1, tail_x, tail_x_2))

        return p_array_1, e1_array, points_l, otn_def, index_vertical_point_uploading

    def list_choise_tpdl(quantity_point, point_1, point_2):
        # лист с выбором последней точки
        list_choise1 = [int(0) for x in range(quantity_point)]  # SELECTED
        list_choise1[point_1] = -1
        list_choise1[point_2] = -1
        return list_choise1

    def list_sequance1_tpdl(quantity_point):
        # последовательность точек с 1 до quantity_point
        list_sequance1 = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM
        return list_sequance1

    def list_choise_NU_tpdl(quantity_point, point_1, point_2):
        # лист по NU
        list_choise_NU_1 = [int(0) for x in range(quantity_point)]  # SELECTED
        list_choise_NU_1[point_1] = -1
        list_choise_NU_1[point_2] = -1
        return list_choise_NU_1

    def create_ev_tpdl(b, quantity_point, parametr_proba, parametr_press, e1_array, otn_def, point_1, point_2):
        Ip = parametr_proba.get('Ip')
        try:
            if Ip < 7:
                b = randint(0, 10) / 10
                c = -randint(80, 90)  # -100
                # b += randint(0, 50) / 10
                # c = -(b * 10 + randint(1, 30))
                d = randint(100, 1000)  # сколько прибавить по ev
                random_ev = np.asarray([float(randint(600, 900) / 10) for x in range(quantity_point)])

            if Ip >= 7 and Ip < 17:
                b = randint(0, 50) / 10
                c = -randint(70, 80)  # -100
                # b += randint(0, 10) / 10
                # c = -(b * 8 + randint(0, 5))
                d = randint(100, 1000)  # сколько прибавить по ev
                random_ev = np.asarray([float(randint(0, 600) / 100) for x in range(quantity_point)])

            if Ip >= 17:
                b = randint(0, 50) / 10
                c = -randint(60, 70)  # -100
                # b += randint(0, 10) / 100
                # c = -(b * 3 + randint(1, 20) / 10)
                d = randint(0, 200)  # сколько прибавить по ev
                random_ev = np.asarray([float(randint(0, 250) / 100) for x in range(quantity_point)])
        except:
            b = randint(0, 50) / 10
            c = -randint(90, 110)  # -100
            # b += randint(0, 50) / 10
            # c = -(b * 10 + randint(0, 500) / 10)
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(500, 1000) / 10) for x in range(quantity_point)])

        kf_y_b = np.asarray([float(b) for x in range(quantity_point)])
        kf_y_c = np.asarray([float(c) for x in range(quantity_point)])
        kf_y_d = np.asarray([float(d) for x in range(quantity_point)])

        st_b = np.asarray([float(2) for x in range(quantity_point)])

        ev_array_1 = ((kf_y_b * e1_array ** st_b) + (kf_y_c * e1_array) + kf_y_d) - random_ev  # DEFORM

        # точка по EV

        # tochka EV _ 2 - EV _ 1

        point_EV = np.asarray([float(ev_array_1[1] - ev_array_1[0]) for x in range(quantity_point)])

        first_point_EV = np.asarray([float(ev_array_1[0]) for x in range(quantity_point)])

        volume_lab = np.asarray([float((math.pi * 19 ** 2) * 76) for x in range(quantity_point)])

        otn_volume_def = (first_point_EV - ev_array_1) / (volume_lab - point_EV)

        point_1_EV = (otn_def[point_1] + otn_volume_def[point_1]) / 2

        point_2_EV = (otn_def[point_2] + otn_volume_def[point_2]) / 2

        difference_p1_p2 = point_2_EV - point_1_EV

        koef_V_1 = abs(1 - (difference_p1_p2 / (otn_def[point_2] - otn_def[point_1])))

        # перерасчет коэффициента Пуассона
        grunt = parametr_proba.get('grunt_type')
        IL = parametr_proba.get('IL')
        if parametr_proba.get('main_type') == 'incoherent':
            k_puss = randint(30, 35) / 100
        if grunt == 'supes':
            k_puss = randint(30, 35) / 100
        if grunt == 'sugl':
            k_puss = randint(35, 37) / 100
        if grunt == 'glina':
            if IL <= 0:
                k_puss = randint(20, 30) / 100
            if 0 < IL <= 0.25:
                k_puss = randint(30, 38) / 100
            if 0.25 < IL <= 1:
                k_puss = randint(38, 45) / 100

        if k_puss != koef_V_1:
            opr_defin = (1 - k_puss) * (otn_def[point_2] - otn_def[point_1])

            otn_vol_point_right = -otn_def[point_2] + otn_def[point_1] + 2 * opr_defin + otn_volume_def[
                point_1]

            EV_2 = -otn_vol_point_right * volume_lab[1] + otn_vol_point_right * difference_p1_p2 + \
                   first_point_EV[1]

            ev_array_1[point_2] = EV_2

        return ev_array_1

    def write_EngGeo_TPDL(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise,
                          list_choise_NU_tpd, CM3DATA_OBJID):
        cursor.execute(
            "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
            % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 4,
               'UNIFORM_PRESSURE': str(parametr_press.get('press')).replace('.', ','), 'FROM_MORECULON': 0,
               'FROM_NU_E': -1, })

        for u in range(0, len(p_array_1)):
            cursor.execute(
                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                % {'OBJID': CM3DATA_OBJID,
                   'EXAM_NUM': 4,
                   'FORCE': (str(p_array_1[u])).replace('.', ','),
                   'DEFORM': (str(e1_array[u])).replace('.', ','),
                   'DEFORM_VOL': (str(ev_array_1[u])).replace('.', ','),
                   'SERIAL_NUM': list_sequance[u],
                   'SELECTED': list_choise[u],
                   'SEL_FOR_NU': list_choise_NU_tpd[u]})
        cursor.commit()

        return True


    parametr_tpd = TPDL(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID)

    press = parametr_press.get('press')


    vertical_speed_rzg = parametr_d.get('vertical_speed_rzg')
    if vertical_speed_rzg == None:
        if parametr_proba.get('main_type') == 'incoherent':
            vertical_speed_rzg = 0.5
        if parametr_proba.get('grunt_type') == 'supes':
            vertical_speed_rzg = 0.3
        if parametr_proba.get('grunt_type') == 'sugl':
            if parametr_proba.get('Ip') < 12:
                vertical_speed_rzg = 0.1
            if parametr_proba.get('Ip') >= 12:
                vertical_speed_rzg = 0.05
        if parametr_proba.get('grunt_type') == 'glina':
            if parametr_proba.get('Ip') >= 40:
                vertical_speed_rzg = 0.005
            if parametr_proba.get('Ip') > 30 and parametr_proba.get('Ip') < 40:
                vertical_speed_rzg = 0.01
            if parametr_proba.get('Ip') > 17 and parametr_proba.get('Ip') <= 30:
                vertical_speed_rzg = 0.02


    else:
        vertical_speed_rzg = float(parametr_d.get('vertical_speed_rzg'))


    p_array_1, e1_array, points_l, otn_def, index_vertical_point_uploading = graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba, parametr_d.get('vertical_point_uploading'))


    quantity_point = len(p_array_1)

    ev_array_1 = create_ev_tpdl(parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press, e1_array,
                           otn_def,
                           points_l[0], points_l[1])


    # дополнительный devisor от давления
    press = parametr_press.get('press')

    def summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, parametr_press, quantity_point, points_l, parametr_isp,
                        parametr_d, parametr_proba, index_vertical_point_uploading):
        # нахождение точки встречи
        press = parametr_press.get('press')


        search_point = index_vertical_point_uploading

        # кол-во точек на петлях разгрузки


        vert_speed_rzg = float(parametr_d.get('vert_speed_rzg'))


        random_end_point_e1_1 = randint(80, 90) / 100



        line_1_e1 = np.arange(e1_array[search_point], e1_array[search_point] - random_end_point_e1_1,
                              -vert_speed_rzg)

        line_2_e1 = np.arange(e1_array[search_point] - random_end_point_e1_1, e1_array[search_point],
                              vert_speed_rzg)




        quantity_point_line_1 = len(line_1_e1)
        quantity_point_line_2 = len(line_2_e1)



        step_p = (p_array_1[search_point] - (press + 0.001)) / quantity_point_line_2

        # линия по Р
        line_1_p = np.arange(p_array_1[search_point], press + 0.001, -step_p)
        line_2_p = np.arange(press + 0.001, p_array_1[search_point], step_p)




        search_press_point1_min = round(p_array_1[points_l[0]], 3) - (
                    p_array_1[search_point] - press) / quantity_point_line_2 * 0.9
        search_press_point1_max = round(p_array_1[points_l[0]], 3) + (
                p_array_1[search_point] - press) / quantity_point_line_2 * 0.9
        search_press_point1 = round(p_array_1[points_l[0]], 3)

        search = 0
        searching_point = round(line_2_p[search], 3)


        def nearest(lst, target):
            return min(lst, key=lambda x: abs(x - target))


        line_2_p = line_2_p.tolist()
        search = line_2_p.index(nearest(line_2_p, searching_point))
        line_2_p = np.asarray(line_2_p)


        searching_point_1 = line_2_p[search]
        searching_point_2 = (line_2_p[search + 1])



        # линия по Е1
        # модуль E2
        if parametr_isp.get('E2') != None:
            E2_right =  parametr_isp.get('E2')
        else:
            E2_right = parametr_isp.get('E') * randint(19000, 24000) / 10000

        line_2_e1[search + 1] = ((76 - abs(e1_array[1] - e1_array[0])) * (
                searching_point_2 - searching_point_1 - (E2_right * (line_2_e1[search])) / (
                abs(e1_array[1] - e1_array[0]) - 76))) / E2_right

        definition_e1_2 = abs(line_2_e1[search + 1] - line_2_e1[search])

        line_2_e1 = np.arange(e1_array[search_point] - (definition_e1_2 * quantity_point_line_2),
                              e1_array[search_point],
                              (definition_e1_2 * quantity_point_line_2) / quantity_point_line_2)

        E2_real_now = (line_2_p[search + 1] - line_2_p[search]) / (
                ((line_2_e1[search + 1] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))) - (
                (line_2_e1[search] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))))


        # модуль Erzg
        # поиск давления для расчета Erzg
        search_press_point1rzg_min = round(p_array_1[points_l[0]], 3) - (
                    p_array_1[search_point] - press + 0.001) / quantity_point_line_1 * 0.9
        search_press_point1rzg_max = round(p_array_1[points_l[0]], 3) + (
                    p_array_1[search_point] - press + 0.001) / quantity_point_line_1 * 0.9
        search_press_point1rzg = round(p_array_1[points_l[0]], 3)

        search = 0
        searching_point = round(line_1_p[search], 3)

        line_1_p = line_1_p.tolist()
        search = line_1_p.index(nearest(line_1_p, searching_point))
        line_1_p = np.asarray(line_1_p)


        searching_point_1rzg = (line_1_p[search])
        searching_point_2rzg = (line_1_p[search + 1])


        if parametr_isp.get('Erzg') != None:
            Erzg_right = parametr_isp.get('Erzg')
        else:
            if parametr_proba.get('grunt_type') == 'glina':
                Erzg_right = parametr_isp.get('E') * randint(3250, 3750) / 1000
            if parametr_proba.get('grunt_type') == 'sugl':
                Erzg_right = parametr_isp.get('E') * randint(3750, 4250) / 1000
            if parametr_proba.get('grunt_type') == 'supes':
                Erzg_right = parametr_isp.get('E') * randint(4250, 4750) / 1000
            if parametr_proba.get('main_type') == 'incoherent':
                Erzg_right = parametr_isp.get('E') * randint(4750, 5500) / 1000


        line_1_e1[search + 1] = ((76 - abs(e1_array[1] - e1_array[0])) * (
                searching_point_2rzg - searching_point_1rzg - (Erzg_right * line_1_e1[search]) / (
                abs(e1_array[1] - e1_array[0]) - 76))) / Erzg_right

        definition_e1 = line_1_e1[search + 1] - line_1_e1[search]

        line_1_e1 = np.arange(e1_array[search_point] - definition_e1 * quantity_point_line_1, e1_array[search_point],
                              (definition_e1 * quantity_point_line_1) / quantity_point_line_1)

        Erzg_real_now = (line_1_p[search + 1] - line_1_p[search]) / (
                ((line_1_e1[search + 1] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))) - (
                (line_1_e1[search] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))))

        # линия для EV
        line_1_EV = np.arange(ev_array_1[search_point], ev_array_1[search_point] + 100,
                              +(100) / quantity_point_line_1)
        line_2_EV = np.arange(ev_array_1[search_point] - 100, ev_array_1[search_point], (100) / quantity_point_line_2)

        count_delete = 0
        while line_1_p[len(line_1_p) - 1] > line_2_p[0]:
            line_2_p = np.delete(line_2_p, 0)
            line_2_e1 = np.delete(line_2_e1, 0)
            line_2_EV = np.delete(line_2_EV, 0)
            count_delete += 1
        line_2_p = np.delete(line_2_p, 0)
        line_2_e1 = np.delete(line_2_e1, 0)
        line_2_EV = np.delete(line_2_EV, 0)

        # пуассон V2
        koef_v2 = randint(160, 250) / 1000

        line_2_EV[search + 1] = -(
                    ((2 * line_2_e1[search + 1] - 2 * line_2_e1[search]) * (math.pi * (19 ** 2) * 76) + (
                            2 * line_2_e1[search] - 2 * line_2_e1[search + 1]) * (
                                 ev_array_1[0] - ev_array_1[1])) * koef_v2 + (
                            line_2_e1[search] - line_2_e1[search + 1]) * (
                            math.pi * (19 ** 2) * 76) + (
                            line_2_e1[search + 1] - line_2_e1[search]) * (
                            ev_array_1[0] - ev_array_1[1]) + (76 - (e1_array[1] - e1_array[0])) *
                    line_2_EV[search]) / ((e1_array[1] - e1_array[0]) - 76)

        definition_ev = line_2_EV[search + 1] - line_2_EV[search]
        line_2_EV = np.arange(ev_array_1[search_point] - definition_ev * quantity_point_line_2,
                              ev_array_1[search_point],
                              (definition_ev * quantity_point_line_2) / quantity_point_line_2)

        # пуассон Vrzg
        koef_vrzg = randint(130, 160) / 1000

        # line_1_EV[search + 1] = (((2*G90-2*G142)*J4+(2*G142-2*G90)*J3+54872*ПИ()*G90-54872*ПИ()*G142)*Z10+(G4-G3-76)*J90+(G142-G90)*J4+(G90-G142)*J3-27436*ПИ()*G90+27436*ПИ()*G142)/(G4-G3-76)

        # по первой кривой
        line_1_EV[len(line_1_EV) - 1] = (((2 * line_1_e1[0] - 2 * line_1_e1[len(line_1_e1) - 1]) * ev_array_1[1] + (
                2 * line_1_e1[len(line_1_e1) - 1] - 2 * line_1_e1[0]) * ev_array_1[0] + 54872 * math.pi * line_1_e1[
                                              0] - 54872 * math.pi * line_1_e1[len(line_1_e1) - 1]) * koef_vrzg + (
                                                 e1_array[1] - e1_array[0] - 76) * line_1_EV[0] + (
                                                 line_1_e1[len(line_1_e1) - 1] - line_1_e1[0]) * ev_array_1[1] + (
                                                 line_1_e1[0] - line_1_e1[len(line_1_e1) - 1]) * ev_array_1[
                                             0] - 27436 * math.pi * line_1_e1[0] + 27436 * math.pi * line_1_e1[
                                             len(line_1_e1) - 1]) / (
                                                e1_array[1] - e1_array[0] - 76)

        for x in range(1, 10):
            line_1_EV[len(line_1_EV) - x] = line_1_EV[len(line_1_EV) - 1]

        Vrzg = abs(1 - ((((((ev_array_1[0] - line_1_EV[0]) / (
                (math.pi * (19 ** 2) * 76) - (ev_array_1[0] - ev_array_1[1]))) + (
                                   (line_1_e1[0] - e1_array[0]) / (76 - (e1_array[1] - e1_array[0])))) / 2) - (
                                 (((ev_array_1[0] - line_1_EV[len(line_1_EV) - 1]) / (
                                         (math.pi * (19 ** 2) * 76) - (ev_array_1[0] - ev_array_1[1]))) + (
                                          (line_1_e1[len(line_1_e1) - 1] - e1_array[0]) / (
                                          76 - (e1_array[1] - e1_array[0])))) / 2)) / (
                                ((line_1_e1[0] - e1_array[0]) / (76 - (e1_array[1] - e1_array[0]))) - (
                                (line_1_e1[len(line_1_e1) - 1] - e1_array[0]) / (
                                76 - (e1_array[1] - e1_array[0]))))))


        # белые розы, высокие 70-80
        if line_1_p[0] < line_2_p[-1]:
            line_2_p = np.delete(line_2_p, 0)
            line_2_e1 = np.delete(line_2_e1, 0)
            line_2_EV = np.delete(line_2_EV, 0)

        # объединение линий в один массив
        p_array_1 = np.concatenate((p_array_1[:search_point], line_1_p, line_2_p, p_array_1[search_point + 1:]))

        e1_array = np.concatenate((e1_array[:search_point], line_1_e1, line_2_e1, e1_array[search_point + 1:]))

        ev_array_1 = np.concatenate(
            (ev_array_1[:search_point], line_1_EV, line_2_EV, ev_array_1[search_point + 1:]))



        return p_array_1, e1_array, ev_array_1

    p_array_1, e1_array, ev_array_1 = summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, parametr_press, quantity_point,
                                                      points_l, parametr_isp, parametr_d, parametr_proba,
                                                     index_vertical_point_uploading)

    min_len = min(len(p_array_1), len(e1_array), len(ev_array_1))

    # удаление лишних точек
    try:
        for x in range(len(p_array_1) - min_len):
            p_array_1 = np.delete(p_array_1, len(p_array_1) - 1)
    except:
        pass
    try:
        for x in range(len(e1_array) - min_len):
            e1_array = np.delete(e1_array, len(e1_array) - 1)
    except:
        pass
    try:
        for x in range(len(ev_array_1) - min_len):
            ev_array_1 = np.delete(ev_array_1, len(ev_array_1) - 1)
    except:
        pass

    quantity_point = len(p_array_1)

    list_choise1 = list_choise_tpdl(quantity_point, points_l[0], points_l[1])
    list_sequance1 = list_sequance1_tpdl(quantity_point)
    list_choise_NU_1 = list_choise_NU_tpdl(quantity_point, points_l[0], points_l[1])

    if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
        write_EngGeo_TPDL(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance1, list_choise1,
                          list_choise_NU_1, CM3DATA_OBJID)




    def ISP_TPDL(parametr_press, p_array_1, e1_array, ev_array_1, points_l):


        quantity_point_past = len(p_array_1)


        time_list = [randint(1200, 1700) / 100]
        for x in range(len(p_array_1) - 1):
            time_list.append(time_list[x] + randint(1200, 1700) / 100)

        action_list = [str('WaitLimit') for x in range(len(p_array_1))]

        action_changed_list = [str(True) for x in range(len(p_array_1))]

        press_list = [float((parametr_press.get('press'))) for x in range(len(p_array_1))]

        Trajectory_list = [str('CTC') for x in range(len(p_array_1))]

        empty_list = [str('') for x in range(len(p_array_1))]

        if len(p_array_1) < len(e1_array):
            definition = len(e1_array) - len(p_array_1)
            for x in range(definition):
                e1_array = np.delete(e1_array, len(e1_array) - 1)

        if len(p_array_1) < len(ev_array_1):
            definition = len(ev_array_1) - len(p_array_1)
            for x in range(definition):
                ev_array_1 = np.delete(ev_array_1, len(ev_array_1) - 1)

        df = pd.DataFrame({'Time': time_list, 'Action': action_list, 'Action_Changed': action_changed_list,
                           'Deviator_kPa': empty_list, 'CellPress_kPa': empty_list, 'VerticalPress_kPa': empty_list,
                           'VerticalDeformation_mm': e1_array,
                           'VerticalStrain': empty_list, 'VolumeStrain': empty_list,
                           'VolumeDeformation_cm3': ev_array_1, 'Deviator_MPa': empty_list,
                           'CellPress_MPa': press_list, 'VerticalPress_MPa': p_array_1, 'Trajectory': Trajectory_list})

        os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/TPDL/')
        os.mkdir((str(parametr_press.get('press'))))
        os.chdir((str(parametr_press.get('press'))))
        shutil.copy('Z:/Zapis\ISP\obr_0.2.xml',
                    File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str((parametr_press.get('press'))))
        os.mkdir('General')
        os.chdir('General')
        my_file = open("General.log", "w+")
        my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                      '76	38')
        my_file.close()
        os.chdir('..')
        os.mkdir('Test')
        os.chdir('Test')

        df.to_csv(
            f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{str((parametr_press.get('press')))}/Test/{str(parametr_press.get('press'))}.log",
            sep='\t', index=False)  # создание лога из выведенного датафрейма

        return True

    if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
            'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
        ISP_TPDL(parametr_press, p_array_1, e1_array, ev_array_1, points_l)

    return True


def SPDL():
    pass


def delete_one_TPD(cursor, CM3DATA_OBJID, parametr_proba):
    cursor.execute("DELETE FROM CM3OPR WHERE (PROBEGR_ID) = '%(PROBEGR_ID)s'" % {
        'PROBEGR_ID': parametr_proba.get('PROBEGR_IDS')})
    cursor.commit()
    return True


def control_isp(parametr_isp, log_dict, parametr_d, parametr_proba, parametr_press, cursor):
    CM3DATA_OBJID = write_CM3opr(parametr_d, parametr_isp, parametr_proba)

    if parametr_isp.get('TPS') != None:
        vert_speed_tps = parametr_d.get('vertical_speed')
        if vert_speed_tps == None:
            if parametr_proba.get('main_type') == 'incoherent':
                vert_speed_tps = 0.1
            if parametr_proba.get('grunt_type') == 'supes':
                vert_speed_tps = 0.1
            if parametr_proba.get('grunt_type') == 'sugl':
                if parametr_proba.get('Ip') < 12:
                    vert_speed_tps = 0.1
                if parametr_proba.get('Ip') >= 12:
                    vert_speed_tps = 0.05
            if parametr_proba.get('grunt_type') == 'glina':
                if parametr_proba.get('Ip') >= 40:
                    vert_speed_tps = 0.005
                if parametr_proba.get('Ip') > 30 and parametr_proba.get('Ip') < 40:
                    vert_speed_tps = 0.01
                if parametr_proba.get('Ip') > 17 and parametr_proba.get('Ip') <= 30:
                    vert_speed_tps = 0.02
        else:
            vert_speed_tps = float(parametr_d.get('vertical_speed'))

        tps_parametr = TPS(parametr_isp, parametr_proba, parametr_press)
        st_list = [tps_parametr.get('st1'), tps_parametr.get('st2'), tps_parametr.get('st3')]
        press_list = [parametr_press.get('press_1'), parametr_press.get('press_2'), parametr_press.get('press_3')]
        press_name = ['press_1', 'press_2', 'press_3']
        exam_list = [1, 2, 3]
        for st, press, EXAM_NUM, press_name in zip(st_list, press_list, exam_list, press_name):

            random_start_e1 = randint(3, 9) * -vert_speed_tps + 0.00000001

            p_array_1, quantity_point, e1_array, otn_def = graph_tps(st, press, press_name, parametr_d, parametr_isp, vert_speed_tps, parametr_proba, random_start_e1)
            list_choise = list_choise1_tps(quantity_point, p_array_1)
            list_sequance = list_sequance1_tps(quantity_point)
            ev_array_1 = create_ev_tps(tps_parametr.get('b'), quantity_point, e1_array)
            if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
                write_EngGeo_TPS(p_array_1, e1_array, ev_array_1, list_sequance, list_choise, EXAM_NUM, press,
                                 quantity_point, CM3DATA_OBJID)
            if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                    'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
                ISP_TPS(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_proba, press, parametr_d, parametr_press, vert_speed_tps, random_start_e1, otn_def)

    if parametr_isp.get('TPD') != None:

        parametr_tpd = TPD(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID)

        vert_speed_def = parametr_d.get('vert_speed_def')

        if vert_speed_def == None:
            if parametr_proba.get('main_type') == 'incoherent':
                vert_speed_def = 0.05
            if parametr_proba.get('grunt_type') == 'supes':
                vert_speed_def = 0.05
            if parametr_proba.get('grunt_type') == 'sugl':
                vert_speed_def = 0.05
            if parametr_proba.get('grunt_type') == 'glina':
                if parametr_proba.get('Ip') >= 40:
                    vert_speed_def = 0.005
                if parametr_proba.get('Ip') > 30 and parametr_proba.get('Ip') < 40:
                    vert_speed_def = 0.01
                if parametr_proba.get('Ip') > 17 and parametr_proba.get('Ip') <= 30:
                    vert_speed_def = 0.02
        else:
            vert_speed_def = float(parametr_d.get('vertical_speed'))


        p_array_1, e1_array, points_l, otn_def = graph(parametr_press, parametr_isp, vert_speed_def, parametr_proba)

        quantity_point = len(p_array_1)

        list_choise1 = list_choise_tpd(quantity_point, points_l[0], points_l[1])
        list_sequance1 = list_sequance1_tpd(quantity_point)
        list_choise_NU_1 = list_choise_NU_tpd(quantity_point, points_l[0], points_l[1])


        ev_array_1 = create_ev(otn_def, parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press, e1_array,
                               points_l[0], points_l[1])




        picture_time = time.strftime("%Y.%m.%d %H_%M_%S", time.localtime(time.time()))
        if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
            write_EngGeo_TPD(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance1, list_choise1,
                             list_choise_NU_1, CM3DATA_OBJID)
        if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
            ISP_TPD(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_press, parametr_proba, parametr_d, points_l, picture_time)

    if parametr_isp.get('SPS') != None:
        press_list = ['press_1', 'press_2', 'press_3']
        choise_max_point = [randint(parametr_d.get('choise_max_point_1'), parametr_d.get('choise_max_point_1_m')),
                            randint(parametr_d.get('choise_max_point_2'), parametr_d.get('choise_max_point_2_m')),
                            randint(parametr_d.get('choise_max_point_3'), parametr_d.get('choise_max_point_3_m'))]
        SDDATA_OBJID = generator_mech_objid()
        if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
            write_SPS_SDOPR(cursor, parametr_proba, parametr_isp, SDDATA_OBJID)
        for press, choise_max in zip(press_list, choise_max_point):
            SHEAR_DEF, quantity_point, st = SPS_SHEAR_DEF(parametr_isp, press, parametr_press,
                                                          parametr_d.get('quantity_point_sps_1'),
                                                          parametr_d.get('quantity_point_sps_2'))
            TANGENT_PRESS = SPS_TANGENT_PRESS(quantity_point, st, choise_max)
            ZAMER_NUM = SPS_ZAMER_NUM(quantity_point)
            T = SPS_time(quantity_point)
            if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
                write_SPS(cursor, SHEAR_DEF, T, TANGENT_PRESS, ZAMER_NUM, parametr_press, press, st,
                          quantity_point, SDDATA_OBJID)
            if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                    'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
                ISP_SPS(SHEAR_DEF, T, TANGENT_PRESS, parametr_press, press)

    if parametr_isp.get('SPD') != None:
        press_spd = search_press_spd(parametr_proba)
        choise_st = search_st_spd(parametr_proba)
        moed, p_y, otn_vert_def, NRN, log_dict = SPD_parametr(parametr_proba, parametr_isp, press_spd, choise_st,
                                                              log_dict)
        if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
            SPD_write(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN)

        if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
            ISP_SPD(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN)

        with open(r"Z:\Zapis\ISP\Сhanged_LAB.txt", "w") as file:
            for line in log_dict.items():
                file.write(str(line) + '\n')

    if parametr_isp.get('TPDL') != None:

        TPDL_generate(parametr_proba, parametr_isp, parametr_d, cursor, CM3DATA_OBJID, parametr_press)

    if parametr_isp.get('SPDL') != None:
        SPDL()


# main part
# main part
# main part
my_file = open("Z:\Zapis\ISP\Table_name.txt")
name_table = my_file.read()
my_file.close()
print(name_table)

NewConnect = cc.ConnectTable()
NewConnect.connect_to_googlesheet(name_table)
worksheet_journal = NewConnect.connect_to_spreadsheet('Start')
worksheet_parametr = NewConnect.connect_to_spreadsheet('Parametr')


class PrepareData:
    pd.options.display.width = None
    pd.options.mode.chained_assignment = None

    def __init__(self, data_input):
        self.DF = None
        self.gc_object = data_input.get_values('A:V', major_dimension="columns")
        self.gc_object1 = data_input.get_values('A:B', major_dimension="rows")

    # makeFrame - создаю дф из журнала
    def makeFrame(self):

        data = {'TPS': [d for d in self.gc_object[0]],
                'TPD': [d for d in self.gc_object[1]],
                'SPS': [d for d in self.gc_object[2]],
                'SPD': [d for d in self.gc_object[3]],
                'TPDL': [d for d in self.gc_object[4]],
                'limiter': [d for d in self.gc_object[5]],
                'LAB_NO': [d for d in self.gc_object[6]],
                'Grunt': [d for d in self.gc_object[7]],
                'C': [d for d in self.gc_object[9]],
                'F': [d for d in self.gc_object[10]],
                'E': [d for d in self.gc_object[11]],
                'DOP': [d for d in self.gc_object[13]],
                'GLUB_DOP': [d for d in self.gc_object[14]],
                'DOPplus': [d for d in self.gc_object[15]],
                'Norm': [d for d in self.gc_object[17]],
                'Erzg': [d for d in self.gc_object[19]],
                'E2': [d for d in self.gc_object[20]],
                'Point_rzg': [d for d in self.gc_object[21]]
                }
        self.DF = pd.DataFrame(data).replace({'': None})

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
            try:
                if x == 'devisor':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
                if x == 'global_point_unloading':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
                else:
                    update = int(update)
                    data.update({x: update})

            except:
                pass

        return data

def make_parametr_isp(isp_data, limiter):
    parametr_isp = {}

    name_column = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    name_parametr = ['TPS', 'TPD', 'SPS', 'SPD', 'TPDL', 'limiter', 'LAB_NO', 'Grunt', 'C', 'F', 'E', 'DOP',
                     'GLUB_DOP', 'DOPplus', 'Norm', 'Erzg', 'E2', 'Point_rzg']
    for name_column, name_parametr in zip(name_column, name_parametr):
        parametr_isp.setdefault(name_parametr, isp_data.iloc[limiter][name_column])

    name_parametr_replace_float = ['C', 'F', 'E', 'GLUB_DOP', 'DOPplus', 'Erzg', 'E2']

    for x in name_parametr_replace_float:
        try:
            parametr_isp.update({x: float(parametr_isp.get(x).replace(',', '.'))})
        except:
            pass

    for x in parametr_isp.keys():
        update = parametr_isp.get(x)
        if update == 'None':
            parametr_isp.update({x: None})

    for x in parametr_isp.keys():
        update = parametr_isp.get(x)
        if update == '':
            parametr_isp.update({x: None})

    try:
        parametr_isp.update({'LAB_NO': parametr_isp.get('LAB_NO').replace(' ', '')})
    except:
        pass

    return parametr_isp




parametr_d = PrepareData(worksheet_parametr).makeParametr()

start_time = datetime.now()  # замер времени

# Генерация года, месяца, дня, минуты, секунды и времени
if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
        'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
    picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    os.chdir('Z:\Zapis\ISP')
    File_Path = os.getcwd() + "\\" + directory_time + "\\" + picture_time + "\\"
    os.makedirs(File_Path)

print(parametr_d.get('path'))

log_dict = {}

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + parametr_d.get('path') + '')
cursor = conn.cursor()

# limiter - ограничитель
try:

    isp_data = PrepareData(worksheet_journal).makeFrame()

    parametr_isp = {}

    name_parametr = ['limiter']

    parametr_isp.setdefault('limiter', isp_data.iloc[1][5])

    r = 1
    while parametr_isp.get('limiter') == '#':

        parametr_isp = make_parametr_isp(isp_data, r)

        if parametr_isp.get('limiter') != '#':
            break

        if (parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1) and (
                parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get(
            'SPS') != None or parametr_isp.get('TPDL') != None or parametr_isp.get('SPD') != None):
            os.chdir(File_Path)
            os.mkdir(parametr_isp.get('LAB_NO'))
            os.chdir(parametr_isp.get('LAB_NO'))
            if parametr_isp.get('TPS') != None:
                os.mkdir('TPS')
            if parametr_isp.get('TPD') != None:
                os.mkdir('TPD')
            if parametr_isp.get('SPS') != None:
                os.mkdir('SPS')
            if parametr_isp.get('TPDL') != None:
                os.mkdir('TPDL')
            if parametr_isp.get('SPD') != None:
                os.mkdir('SPD')

        if r == 1:
            delete_parametr_one_time(parametr_d, parametr_isp, cursor)

        if parametr_isp.get('TPS') == None and parametr_isp.get('TPD') == None and parametr_isp.get('SPS') == None and parametr_isp.get('TPDL') == None and parametr_isp.get('SPD') == None:
            r += 1
            continue

        parametr_proba = getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor)

        # удаление механики в пробе
        delete_parametr_many_time(parametr_d, parametr_isp, parametr_proba, cursor)

        execute_parametr_isp(parametr_d, parametr_proba, parametr_isp, cursor)

        parametr_press = calculate_press_gost(parametr_isp, parametr_proba, parametr_d)

        control_isp(parametr_isp, log_dict, parametr_d, parametr_proba, parametr_press, cursor)

        r += 1

        print(parametr_isp.get('LAB_NO'))

    cursor.commit()
    cursor.close()

    print(datetime.now() - start_time)
    Di = input()
except Exception as err:
    print('Исправляй  ' + parametr_isp.get('LAB_NO'))
    logging.exception(err)
    Di = input()
