from random import randint
import math
import os
import shutil
import sys
import time

import numpy as np
import pandas as pd
import pyodbc

sys.setrecursionlimit(30000)

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


def ISP_SPS(File_Path, SHEAR_DEF, T, TANGENT_PRESS, parametr_press, press, parametr_isp):

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