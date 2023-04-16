import random
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


def SPD_parametr(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, cursor):
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
        # кольца
        rings = {}
        select = "SELECT OBJID,P,V,NUM FROM Rings WHERE P > 50"
        OBJID_RING = list(cursor.execute(select).fetchall())
        for x in range(len(OBJID_RING)):
            rings.setdefault(OBJID_RING[x][0], [OBJID_RING[x][1], OBJID_RING[x][2], OBJID_RING[x][3]])
        ring_list = list(rings.keys())
        RING_OBJID = random.choice(ring_list)
        VES_0 = rings.get(RING_OBJID)[0]
        OBJEM_0 = rings.get(RING_OBJID)[1]

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

    degree_d = randint(4, 6) / 10

    a = delta_h / ((0.2 ** degree_d) - (0.1 ** degree_d))

    # расчет точек по y, т.е. давления в миллиметрах
    p_y = []
    for x in press_spd:
        p_y.append(a * x ** degree_d)

    p_y = np.asarray(p_y)

    # p_y = np.arange(0, delta_h * len(press_spd), delta_h)
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


def SPD_write(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN, cursor):
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


def ISP_SPD(parametr_proba, parametr_isp, press_spd, choise_st, log_dict, moed, p_y, otn_vert_def, NRN, File_Path):
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

