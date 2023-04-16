from random import randint
import math
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyodbc

sys.setrecursionlimit(30000)
# трехосная прочность
# трехосная прочность
# трехосная прочность
"""
Суть в том, чтобы сделать прочность, на которой можно было бы найти модуль деформации, 
так как это позволяет решить сразу следующие проблемы:

1) Использовать методику Мирного по определению параметров для HS
2) Уменьшить избыточность информации
3) Решать что нужно иметь в качестве выхода после работы с модулем (а- 3 графика, на которых определяется прочность и
модули
б- 4 графика, где 3 предназначены для определения прочности с модулями и 1 график для разгрузки)

4) Иметь графики, которые похожи на реальные в плане их сходимости, ведь прочность и деформвция одно и тоже не так ли?
"""

def make_TPS_parametr(parametr_isp, parametr_proba, parametr_press):
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
    st2 = parametr_press.get('press_2')*(2*math.tan(math.pi*parametr_isp.get('F')/180)*((((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))+2*((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)+(2*((2*math.tan(math.pi*parametr_isp.get('F')/180)*((((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))+2*((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))*parametr_isp.get('C'))


        # (((st1 + st3) / 2) * (
        #     parametr_press.get('press_2') / ((parametr_press.get('press_3') + parametr_press.get('press_1')) / 2)))

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

    if parametr_proba.get('main_type') == 'incoherent' and parametr_d.get('need_tail') == 2:

        first_point_tail = randint(5, 6) / 100
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
        g = randint(10,20) / 10

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
        if parametr_proba.get('main_type') == 'incoherent':
            curve = randint(10, 30) / 100
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

    # последовательность точек с 1 до quantity_point
    list_sequance = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM
    return list_choise, list_sequance


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
                     CM3DATA_OBJID, cursor):

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
           'FROM_NU_E': -1, 'FROM_HS': -1, 'FROM_PSI': -1})

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


def ISP_TPS(File_Path, p_array_1, e1_array, ev_array_1, parametr_isp, parametr_proba, press, parametr_d, parametr_press, vert_speed, random_start_e1, otn_def, picture_time, EXAM_NUM):

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

    EXAM_NUM = str(EXAM_NUM)
    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/TPDL/')
    os.mkdir(picture_time + EXAM_NUM)
    os.chdir(picture_time + EXAM_NUM)

    shutil.copy('Z:/Zapis\ISP\obr_TPD.xml',
                File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time + EXAM_NUM))
    os.rename(f"{File_Path}{parametr_isp.get('LAB_NO')}/TPDL/{str(picture_time + EXAM_NUM)}/obr_TPD.xml",
              f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{picture_time + EXAM_NUM}" + f"/{picture_time}.xml")

    os.mkdir('Execute')
    os.chdir('Execute')
    with open(
            fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time + EXAM_NUM) + '/Execute/' + 'Execute.1.log'}",
            "w") as file:
        for key in log_Execute.keys():
            file.write(str(log_Execute.get(key)) + '\n')
    os.chdir('..')

    os.mkdir('General')
    os.chdir('General')
    with open(
            fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time + EXAM_NUM) + '/General/' + 'General.1.log'}",
            "w") as file:
        for key in log_General.keys():
            file.write(str(log_General.get(key)) + '\n')

    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{str(picture_time + EXAM_NUM)}/Test/{'Test.1'}.log",
        sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True
