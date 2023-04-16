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

import HS
import main_tools

# создание параметров пробы на основе инжгео


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
            'INSERT INTO CM3OPR (OBJID,	PROBEGR_ID,	DATE_TEST,	TEST_SCHEME,	STOCK_AREA,	AREA,	HEIGHT,	ZOOM_PERCENT,	PRIBOR_OBJID) '
            + 'VALUES (?,?,?,?,?,?,?,?,?)')
    write_2 = cursor.execute(write_1, CM3DATA_OBJID, parametr_proba.get('PROBEGR_IDS'),
                             directory_time, 2, -777777, 1134.115, 76,
                             randint(60, 70), 'F70EC2ACDCCA4FB19C2C16C0DAD8CD38')
    cursor.commit()
    return CM3DATA_OBJID


# вычисление параметров давления и К_0 (деформация, прочность, срез)
def calculate_press_gost(parametr_isp, parametr_proba, parametr_d):
    if parametr_proba.get('GLUB') < 5:
        press_1 = 0.06103
        press_2 = 0.05 + 0.15
        press_3 = press_2 + 0.15

    else:
        press_1 = (parametr_proba.get('GLUB') * 10) / 1000
        press_2 = press_1 + 0.15
        press_3 = press_2 + 0.15

    parametr_press = {'press_1': press_1, 'press_2': press_2, 'press_3': press_3}

    return parametr_press


# execute - выполнить
# выполнить параметры испытания (очистка сводок)
def execute_parametr_isp(parametr_d, parametr_proba, parametr_isp, cursor):
    # Нужно ли проставить значения автоматически? (нормативные)
    if parametr_d.get('parametr_normativka') == 1:
        normative_value = main_tools.normative_parametr_isp(parametr_proba)
        for value in 'C', 'F', 'E':
            parametr_isp.update({value: normative_value.get(value)})
    else:
        if parametr_isp.get('Norm') != None:
            # выбор проб для автомата
            normative_value = main_tools.normative_parametr_isp(parametr_proba)
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

def delete_one_TPD(cursor, CM3DATA_OBJID, parametr_proba):
    cursor.execute("DELETE FROM CM3OPR WHERE (PROBEGR_ID) = '%(PROBEGR_ID)s'" % {
        'PROBEGR_ID': parametr_proba.get('PROBEGR_IDS')})
    cursor.commit()
    return True


def control_isp(parametr_isp, log_dict, parametr_d, parametr_proba, parametr_press, cursor):

    CM3DATA_OBJID = write_CM3opr(parametr_d, parametr_isp, parametr_proba)

    tps_parametr = HS.make_TPS_parametr(parametr_isp, parametr_proba, parametr_press)
    st_list = [tps_parametr.get('st1'), tps_parametr.get('st2'), tps_parametr.get('st3')]
    press_list = [parametr_press.get('press_1'), parametr_press.get('press_2'), parametr_press.get('press_3')]
    press_name = ['press_1', 'press_2', 'press_3']
    exam_list = [1, 2, 3]

    # if parametr_isp.get('TPDL') != None:
    # if parametr_isp.get('TPDL') != None:
    # if parametr_isp.get('TPDL') != None:
    parametr_tpd = HS.TPDL(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID)

    press = press_list[0]

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

    p_array_1, e1_array, points_l, otn_def, index_vertical_point_uploading, vertical_speed_rzg = HS.graph_tpdl(parametr_d, press, parametr_isp, vertical_speed_rzg, parametr_proba, parametr_d.get(
                                                                                                'vertical_point_uploading'), st_list[0])
    quantity_point = len(p_array_1)
    ev_array_1 = HS.create_ev_tpdl(parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press,
                                         e1_array,
                                         otn_def,
                                         points_l[0], points_l[1])

    p_array_1, e1_array, ev_array_1 = HS.summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, press,
                                                               quantity_point,
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

    list_choise1, list_sequance1, list_choise_NU_1 = HS.list_choise_tpdl(quantity_point, points_l[0], points_l[1], p_array_1)

    EXAM_NUM = 1


    if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
        HS.write_EngGeo_TPDL(cursor, press, p_array_1, e1_array, ev_array_1, list_sequance1,
                                   list_choise1,
                                   list_choise_NU_1, CM3DATA_OBJID, EXAM_NUM)

    if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
            'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
        HS.ISP_TPDL(press, p_array_1, e1_array, ev_array_1, points_l, File_Path, parametr_isp)


    print('1 график готов')



    # ОСТАВШИЕСЯ 2 ГРАФИКА
    # ОСТАВШИЕСЯ 2 ГРАФИКА
    # ОСТАВШИЕСЯ 2 ГРАФИКА# ОСТАВШИЕСЯ 2 ГРАФИКА# ОСТАВШИЕСЯ 2 ГРАФИКА
    # ОСТАВШИЕСЯ 2 ГРАФИКА
    # ОСТАВШИЕСЯ 2 ГРАФИКА
    for press, st, EXAM_NUM in zip(press_list, st_list, exam_list):
        if press_list.index(press) == 0:
            continue

        parametr_tpd = HS.TPDs(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID)

        curve_test_max = 0.001

        max_choise_p = press * 1.8

        p_array_1, e1_array, points_l, otn_def = HS.graph_tpds(parametr_d, press,
                                                                                               parametr_isp,
                                                                                               vertical_speed_rzg,
                                                                                               parametr_proba,
                                                                                               parametr_d.get(
                                                                                                   'vertical_point_uploading'),
                                                                                               st, curve_test_max, max_choise_p)

        min_len = min(len(p_array_1), len(e1_array))

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
        quantity_point = len(p_array_1)

        ev_array_1 = HS.create_ev_tpds(parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press,
                                       e1_array,
                                       otn_def,
                                       points_l[0], points_l[1])


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

        list_choise1, list_sequance1, list_choise_NU_1 = HS.list_choise_tpds(quantity_point, points_l[0], points_l[1])

        if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
            HS.write_EngGeo_TPDs(cursor, press, p_array_1, e1_array, ev_array_1, list_sequance1,
                                 list_choise1,
                                 list_choise_NU_1, CM3DATA_OBJID, EXAM_NUM)

        print(f'{EXAM_NUM} график готов')
        if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
            HS.ISP_TPDS(File_Path, p_array_1, e1_array, ev_array_1, parametr_isp, press, parametr_proba, parametr_d,
                    points_l, picture_time, EXAM_NUM)

    # компрессия
    # компрессия
    # компрессия
    # компрессия
    moed, p_y, otn_vert_def, NRN, log_dict, press_spd, choise_st = HS.SPD_parametr(parametr_proba, parametr_isp, log_dict, cursor)
    if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
        HS.SPD_write(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN, cursor)
    if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
            'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
        HS.ISP_SPD(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN, File_Path)
    with open(r"Z:\Zapis\ISP\Сhanged_LAB.txt", "w") as file:
        for line in log_dict.items():
            file.write(str(line) + '\n')


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
                'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1):
            os.chdir(File_Path)
            os.mkdir(parametr_isp.get('LAB_NO'))
            os.chdir(parametr_isp.get('LAB_NO'))

            os.mkdir('TPDL')
            os.mkdir('TPDS')
            os.mkdir('SPD')

        if r == 1:
            delete_parametr_one_time(parametr_d, parametr_isp, cursor)

        if parametr_isp.get('TPS') == None and parametr_isp.get('TPD') == None and parametr_isp.get('SPS') == None and parametr_isp.get('TPDL') == None and parametr_isp.get('SPD') == None:
            r += 1
            continue

        parametr_proba = main_tools.getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor)

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
