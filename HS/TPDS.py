from random import randint
import math
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyodbc

sys.setrecursionlimit(30000)


"""
Отличается от обычной копрессии в механике, тем, что у нее фиксированное количество ступеней от 0.05 до 1.2 Мпа
И тем что у нее весь грунт, вне зависимости от его Sr, находиться в природной влажности.
Природная влажность нужна для того, чтобы показывался метод Беккера и Казагренде для OCR и переуплотнения и т.д.


Модуль Emoed этой компресси не нужен, так как есть одометрический Eoed на котором завязаны показатели HS
"""
# деформация c разгрузкой
def TPDs(parametr_d, parametr_isp, parametr_proba, parametr_press, CM3DATA_OBJID):
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



def graph_tpds(parametr_d, press, parametr_isp, vertical_speed_rzg, parametr_proba, vertical_point_uploading, st, curve_test_max, max_choise_p):

    E = parametr_isp.get('E')

    e1_array = np.arange(0.00001, 11.4, vertical_speed_rzg)



    first_point_e1 = np.asarray([float(e1_array[0]) for x in range(len(e1_array))])
    raznitsa_fistr_second_e1 = np.asarray(
        [float(e1_array[1] - e1_array[0]) for x in range(len(e1_array))])
    list_76 = np.asarray([float(76) for x in range(len(e1_array))])
    otn_def = (e1_array - first_point_e1) / (list_76 - raznitsa_fistr_second_e1)


    index_vertical_point_uploading = len(otn_def) - 1

    press_list = np.asarray([float(press) for x in range(len(e1_array))])






    last_point_1 = st

    # проверка на минимальный модуль
    # проверка на минимальный модуль
    # проверка на минимальный модуль
    # проверка на минимальный модуль
    curve_test_min = 50000

    c_1 = last_point_1 / (math.atan(((e1_array[-1] / curve_test_min)) ** 0.5)) - press / (math.atan(((e1_array[-1] / curve_test_min)) ** 0.5))

    p_array_1 = []

    for x in e1_array:
        p_array_1.append(c_1 * math.atan((x / curve_test_min) ** 0.5) + press)

    # max_choise_p = press * 1.6

    # если не хватает модуля на curve, то нужно отодвинуть точку разгруки в большую сторону

    list_module_min = []
    for x in range(len(e1_array)):
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


    c_1 = (last_point_1 / (math.atan(((e1_array[-1] / curve_test_max)) ** 0.5)) - (
            press / (math.atan(((e1_array[-1] / curve_test_max)) ** 0.5))))

    p_array_1 = []

    for x in e1_array:
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

        if curve_test_max > 0.2:
            curve_test_max = 0.001

            vertical_speed_rzg_list = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.001]

            vertical_speed_rzg_now = vertical_speed_rzg_list.index(vertical_speed_rzg)

            try:
                vertical_speed_rzg = vertical_speed_rzg_list[vertical_speed_rzg_now + 1]
            except:
                print(press, '  ', last_point_1, '  ', E)
                exit()



        curve_test_max += 0.005
        return graph_tpds(parametr_d, press,parametr_isp, vertical_speed_rzg, parametr_proba, parametr_d.get('vertical_point_uploading'), st, curve_test_max, max_choise_p)

    E_now = round(list_module_max[point_1], 2)

    E_now_past = round(list_module_max[point_1], 2)

    count = 0

    while E != E_now:

        c_1 = (last_point_1 / (math.atan(((e1_array[-1] / curve_test_max)) ** 0.5)) - (
                press / (math.atan(((e1_array[-1] / curve_test_max)) ** 0.5))))

        p_array_1 = []

        for x in e1_array:
            p_array_1.append(c_1 * math.atan((x / curve_test_max) ** 0.5) + press)

        # max_choise_p = press * 1.6

        # если не хватает модуля на curve, то нужно отодвинуть точку разгруки в большую сторону

        list_module = []
        for x in range(len(e1_array)):
            list_module.append((p_array_1[x + 1] - p_array_1[x]) / abs(otn_def[x + 1] - otn_def[x]))
            if x + 1 > point_1:
                break

        E_now = round(list_module[point_1], 2)

        # print(E_now, '    ', count)

        if E == E_now:
            break

        curve_test_max += 0.0001
        count += 1

        if count > 20000:
            curve_test_max += 0.001

        if count > 40000:
            curve_test_max += 0.01


    return p_array_1, e1_array, points_l, otn_def


def list_choise_tpds(quantity_point, point_1, point_2):
        # лист с выбором последней точки
        list_choise1 = [int(0) for x in range(quantity_point)]  # SELECTED
        list_choise1[point_1] = -1
        list_choise1[point_2] = -1


        # последовательность точек с 1 до quantity_point
        list_sequance1 = [int(x) for x in range(1, quantity_point + 1)]  # SERIAL_NUM


        # лист по NU
        list_choise_NU_1 = [int(0) for x in range(quantity_point)]  # SELECTED
        list_choise_NU_1[point_1] = -1
        list_choise_NU_1[point_2] = -1

        return list_choise1, list_sequance1, list_choise_NU_1


def create_ev_tpds(b, quantity_point, parametr_proba, parametr_press, e1_array, otn_def, point_1, point_2):
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

def write_EngGeo_TPDs(cursor, press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise,
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




def ISP_TPDS(File_Path, p_array_1, e1_array, ev_array_1, parametr_isp, press, parametr_proba, parametr_d, points_l, picture_time, EXAM_NUM):


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

    EXAM_NUM = str(EXAM_NUM)
    os.chdir(File_Path + parametr_isp.get('LAB_NO') + '/TPDL/')
    os.mkdir(picture_time+EXAM_NUM)
    os.chdir(picture_time+EXAM_NUM)



    shutil.copy('Z:/Zapis\ISP\obr_TPD.xml',
                File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time+EXAM_NUM))
    os.rename(f"{File_Path}{parametr_isp.get('LAB_NO')}/TPDL/{str(picture_time+EXAM_NUM)}/obr_TPD.xml", f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{picture_time+EXAM_NUM}" + f"/{picture_time}.xml")





    os.mkdir('Execute')
    os.chdir('Execute')
    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time+EXAM_NUM) + '/Execute/' + 'Execute.1.log'}",
              "w") as file:
        for key in log_Execute.keys():
            file.write(str(log_Execute.get(key)) + '\n')
    os.chdir('..')

    os.mkdir('General')
    os.chdir('General')
    with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPDL/' + str(picture_time+EXAM_NUM) + '/General/' + 'General.1.log'}",
              "w") as file:
        for key in log_General.keys():
            file.write(str(log_General.get(key)) + '\n')


    os.chdir('..')
    os.mkdir('Test')
    os.chdir('Test')

    df.to_csv(
        f"{File_Path + parametr_isp.get('LAB_NO')}/TPDL/{str(picture_time+EXAM_NUM)}/Test/{'Test.1'}.log",
        sep='\t', index=False)  # создание лога из выведенного датафрейма

    return True