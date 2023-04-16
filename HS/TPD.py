from random import randint
import math
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyodbc

sys.setrecursionlimit(30000)
# трехосная деформация
# трехосная деформация
# трехосная деформация
"""
Отличается от обычной копрессии в механике, тем, что у нее фиксированное количество ступеней от 0.05 до 1.2 Мпа
И тем что у нее весь грунт, вне зависимости от его Sr, находиться в природной влажности.
Природная влажность нужна для того, чтобы показывался метод Беккера и Казагренде для OCR и переуплотнения и т.д.


Модуль Emoed этой компресси не нужен, так как есть одометрический Eoed на котором завязаны показатели HS
"""

def make_TPD_parametr(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID):
    press = parametr_press.get('press') # давление на образец
    E = parametr_isp.get('E') # модуль пробы

    # определение скорости вертикальной деформации и коэффициента Пуассона
    vert_speed_def = parametr_d.get('vert_speed_def') # скорость вертикальной деформации
    koef_Puasson = parametr_isp.get('Puasson')  # заданный коэффициент Пуассона
    if vert_speed_def == None:
        if parametr_proba.get('main_type') == 'incoherent':
            vert_speed_def = 0.05
            increment_volume = randint(1, 10) / 1000 # приращение объема в процессе стабилизации образца
            koef_Puasson = randint(30, 35) / 100

        if parametr_proba.get('grunt_type') == 'supes':
            vert_speed_def = 0.05
            increment_volume = randint(1, 2) / 1000 # приращение объема в процессе стабилизации образца
            koef_Puasson = randint(30, 35) / 100

        if parametr_proba.get('grunt_type') == 'sugl':
            vert_speed_def = 0.05
            increment_volume = randint(30, 60) / 1000 # приращение объема в процессе стабилизации образцa
            koef_Puasson = randint(35, 37) / 100

        if parametr_proba.get('grunt_type') == 'glina':
            if parametr_proba.get('Ip') >= 40:
                vert_speed_def = 0.005
            if parametr_proba.get('Ip') > 30 and parametr_proba.get('Ip') < 40:
                vert_speed_def = 0.01
            if parametr_proba.get('Ip') > 17 and parametr_proba.get('Ip') <= 30:
                vert_speed_def = 0.02
            increment_volume = randint(2, 3) / 1000 # приращение объема в процессе стабилизации образца

            IL = parametr_proba.get('IL')
            if IL <= 0:
                koef_Puasson = randint(20, 30) / 100
            if 0 < IL <= 0.25:
                koef_Puasson = randint(30, 38) / 100
            if 0.25 < IL <= 1:
                koef_Puasson = randint(38, 45) / 100
    else:
        vert_speed_def = float(parametr_d.get('vertical_speed'))


    percent_max_def_proba = 15 if parametr_d.get('percent_max_def_proba') == None else parametr_d.get('percent_max_def_proba') # критерий разрушения образца в процентах (целое)
    height_proba = 76 if parametr_d.get('height_proba') == None else parametr_d.get('height_proba') # высота образца в мм
    base_proba = 38 if parametr_d.get('base_proba') == None else parametr_d.get('base_proba') # основание образца в мм
    square_proba = 2 * math.pi * (base_proba / 2) * (height_proba + base_proba / 2) # площадь образца в мм2
    volume_proba = math.pi * (base_proba / 2) ** 2 * height_proba # объем образца
    last_point_e1 = (percent_max_def_proba / 100) * height_proba # последняя точка для e1_array


    # ПОКА НЕ РАБОТАЕТ, ТАК КАК ЭТО ПРИРАЩЕНИЕ ОТНОСИТЕЛЬНОЙ ОБЪЕМНОЙ ДЕФОРМАЦИИ

    # в процессе приращения объема образца после стабилизации требуется вычислить объем и изменение высоты образца,
    # которая в случае стремления к положительному углу дилатансии будет уменьшаться, так как объем будет изменяться
    # в отрицательную сторону, значит принимаем тот же радиус основания, указанный в параметрах пробы и вычисляем высоту
    # образца после стадии стабилизации
    height_after_stabilization = (4 * (volume_proba + increment_volume)) / (math.pi * base_proba ** 2)
    # ее можно использовать чтобы вычислить разницу в исходнике при старте испытания, а также использовать ее
    # при вычислении правильной относительной деформации всего испытания

    e1_array = np.arange(0.0000001, last_point_e1, vert_speed_def) # массив E1 в мм

    list_76 = np.asarray([float(height_proba) for x in range(len(e1_array))]) # массив высоты пробы
    otn_def = (e1_array) / (list_76) # относительная деформация


    parametr_tpd = {'press': press, 'E': E, 'koef_Puasson': koef_Puasson, 'vert_speed': vert_speed_def,
                    'koef_Puasson': koef_Puasson, 'height_after_stabilization': height_after_stabilization,
                    'e1_array': e1_array, 'otn_def': otn_def}

    return parametr_tpd



def graph_TPD(parametr_tpd, parametr_proba, parametr_d):

    # распаковка необходимых параметров
    press = parametr_tpd.get('press')
    E = parametr_tpd.get('E')
    vert_speed = parametr_tpd.get('vert_speed')
    e1_array = parametr_tpd.get('e1_array')
    otn_def = parametr_tpd.get('otn_def')


    koef_vert_speed = vert_speed / 0.02

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

    quantity_point = len(p_array_1)


    return p_array_1, e1_array, points_l, quantity_point


def list_choise_tpd(quantity_point, point_1, point_2):
    # лист с выбором последней точки
    list_choise1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise1[point_1] = -1
    list_choise1[point_2] = -1

    list_sequance1 = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM

    # лист по NU
    list_choise_NU_1 = [int(0) for x in range(quantity_point)]  # SELECTED
    list_choise_NU_1[point_1] = -1
    list_choise_NU_1[point_2] = -1
    return list_choise1, list_sequance1, list_choise_NU_1


def create_ev_tpd(parametr_tpd, parametr_proba, quantity_point, point_1, point_2):
    k_puss = parametr_tpd.get('koef_Puasson')
    e1_array = parametr_tpd.get('e1_array')
    otn_def = parametr_tpd.get('otn_def')
    Ip = parametr_proba.get('Ip')
    try:
        if Ip < 7:
            b = randint(300, 400) / 10 + randint(0, 50) / 10
            c = -(b * 10 + randint(1, 30))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(600, 900) / 10) for x in range(quantity_point)])

        if Ip >= 7 and Ip < 17:
            b = randint(50, 100) / 10 + randint(0, 10) / 10
            c = -(b * 8 + randint(0, 5))
            d = randint(100, 1000)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 600) / 100) for x in range(quantity_point)])

        if Ip >= 17:
            b = randint(1, 15) / 10 + randint(0, 10) / 100
            c = -(b * 3 + randint(1, 20) / 10)
            d = randint(0, 200)  # сколько прибавить по ev
            random_ev = np.asarray([float(randint(0, 250) / 100) for x in range(quantity_point)])
    except:
        b = randint(300, 400) / 10 + randint(0, 50) / 10
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
    if k_puss != koef_V_1:
        opr_defin = (1 - k_puss) * (otn_def[point_2] - otn_def[point_1])

        otn_vol_point_right = -otn_def[point_2] + otn_def[point_1] + 2 * opr_defin + otn_volume_def[
            point_1]

        EV_2 = -otn_vol_point_right * volume_lab[1] + otn_vol_point_right * difference_p1_p2 + \
               first_point_EV[1]

        ev_array_1[point_2] = EV_2

    return ev_array_1


def write_EngGeo_TPD(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise, list_choise_NU_tpd,
                     CM3DATA_OBJID, cursor):


    cursor.execute(
        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 4,
           'UNIFORM_PRESSURE': str(parametr_press.get('press') * 1.95).replace('.', ','), 'FROM_MORECULON': 0,
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


def ISP_TPD(File_Path, p_array_1, e1_array, ev_array_1, parametr_isp, parametr_press, parametr_proba, parametr_d, points_l, picture_time):
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


    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPD/{str(picture_time)}/Test/{'Test.1'}.log",
        sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True