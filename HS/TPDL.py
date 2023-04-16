from random import randint
import math
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyodbc

sys.setrecursionlimit(100000)


"""
Отличается от обычной копрессии в механике, тем, что у нее фиксированное количество ступеней от 0.05 до 1.2 Мпа
И тем что у нее весь грунт, вне зависимости от его Sr, находиться в природной влажности.
Природная влажность нужна для того, чтобы показывался метод Беккера и Казагренде для OCR и переуплотнения и т.д.


Модуль Emoed этой компресси не нужен, так как есть одометрический Eoed на котором завязаны показатели HS
"""
# деформация c разгрузкой
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



def graph_tpdl(parametr_d, press, parametr_isp, vertical_speed_rzg, parametr_proba, vertical_point_uploading, st):

    if vertical_point_uploading == 0.075:
        vertical_point_uploading = 0.02

        vertical_speed_rzg_list = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.001]

        vertical_speed_rzg_now = vertical_speed_rzg_list.index(vertical_speed_rzg)

        try:
            vertical_speed_rzg = vertical_speed_rzg_list[vertical_speed_rzg_now + 1]
        except:
            print('Невозможно')


        return graph_tpdl(parametr_d, press, parametr_isp, vertical_speed_rzg, parametr_proba,
                          vertical_point_uploading, st)

    E = parametr_isp.get('E')

    e1_array = np.arange(0.00001, 11.4, vertical_speed_rzg)


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
    if press < 100:
        curve_test_max = 0.1
    elif press < 200:
        curve_test_max = 0.2
    else:
        curve_test_max = 0.3

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

        return graph_tpdl(parametr_d, press, parametr_isp, vertical_speed_rzg, parametr_proba,
                          vertical_point_uploading, st)


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

        if E == E_now:
            break

        curve_test_max += 0.00001
        count += 1

        if count > 20000:
            curve_test_max += 0.0001

        if count > 40000:
            curve_test_max += 0.001




    # вторая часть графика
    # вторая часть графика
    # вторая часть графика
    # вторая часть графика
    e1_array_second = e1_array[index_vertical_point_uploading:]

    last_point_2 = st

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

    return p_array_1, e1_array, points_l, otn_def, index_vertical_point_uploading, vertical_speed_rzg

def list_choise_tpdl(quantity_point, point_1, point_2, p_array_1):
    # лист с выбором последней точки
    list_choise1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise1[point_1] = -1
    list_choise1[point_2] = -1

    point_press_in_p1array = p_array_1[point_1]
    def nearest(lst, target):
        return min(lst, key=lambda x: abs(x - target))
    p_array_1 = p_array_1.tolist()[point_2 + 1:]
    search = p_array_1.index(nearest(p_array_1, point_press_in_p1array)) + point_2
    p_array_1 = np.asarray(p_array_1)

    list_choise1[search] = -1
    list_choise1[search + 1] = -1
    list_choise1[-1] = -1

    # последовательность точек с 1 до quantity_point
    list_sequance1 = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM


    # лист по NU
    list_choise_NU_1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise_NU_1[point_1] = -1
    list_choise_NU_1[point_2] = -1
    list_choise_NU_1[search] = -1
    list_choise_NU_1[search + 1] = -1
    list_choise_NU_1[-1] = -1


    def nearest(lst, target):
        return min(lst, key=lambda x: abs(x - target))

    return list_choise1, list_sequance1, list_choise_NU_1


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

def write_EngGeo_TPDL(cursor, press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise,
                      list_choise_NU_tpd, CM3DATA_OBJID, EXAM_NUM):
    cursor.execute(
        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME, FROM_HS, FROM_PSI) "
        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s', '1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1', '%(FROM_HS)s', '%(FROM_PSI)s')"
        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': EXAM_NUM,
           'UNIFORM_PRESSURE': str(press).replace('.', ','), 'FROM_MORECULON': -1,
           'FROM_NU_E': -1, 'FROM_HS': -1, 'FROM_PSI': -1})

    for u in range(0, len(p_array_1)):
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
               'SEL_FOR_NU': list_choise_NU_tpd[u]})
    cursor.commit()

    return True


def summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, press, quantity_point, points_l, parametr_isp,
                    parametr_d, parametr_proba, index_vertical_point_uploading):
    # нахождение точки встречи

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



    search = 0
    searching_point = round(line_2_p[search], 3)


    def nearest(lst, target):
        return min(lst, key=lambda x: abs(x - target))


    line_2_p = line_2_p.tolist()
    search = line_2_p.index(nearest(line_2_p, searching_point))
    line_2_p = np.asarray(line_2_p)


    searching_point_1 = line_2_p[search]
    searching_point_2 = (line_2_p[search + 1])

    searching_point_SPEC = line_2_p[search]



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



def ISP_TPDL(press, p_array_1, e1_array, ev_array_1, points_l, File_Path, parametr_isp):

    quantity_point_past = len(p_array_1)

    time_list = [randint(1200, 1700) / 100]
    for x in range(len(p_array_1) - 1):
        time_list.append(time_list[x] + randint(1200, 1700) / 100)

    action_list = [str('WaitLimit') for x in range(len(p_array_1))]

    action_changed_list = [str(True) for x in range(len(p_array_1))]

    press_list = [float((press)) for x in range(len(p_array_1))]

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
    os.mkdir((str(press)))
    os.chdir((str(press)))
    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml',
                File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str((press)))
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
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{str((press))}/Test/{str(press)}.log",
        sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True
