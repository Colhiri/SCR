import time
import os
import shutil
import math
import random
from datetime import datetime
import logging
from random import randint
import pandas as pd
import xlwings as xw
import pyodbc
from numba import jit

start_time = datetime.now() #замер времени
my_file = open("Z:\Zapis\ISP\DATA\Select_base.txt")

PUTIN=my_file.read()
my_file.close()
print(PUTIN)

# Генерация года, месяца, дня, минуты, секунды и времени
picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
os.chdir('Z:\Zapis\ISP')
File_Path = os.getcwd() + "\\" + directory_time + "\\" + picture_time + "\\"
os.makedirs(File_Path)

wbxl = xw.Book('Z:/Zapis/ISP/Shablon.xlsx')
if wbxl.sheets['Parametr'].range('A1').value=='+':
    not_create_ISP=1
if wbxl.sheets['Parametr'].range('A1').value==None:
    not_create_ISP=0

if wbxl.sheets['Parametr'].range('A2').value=='+':
    not_write_EngGeo = 1
if wbxl.sheets['Parametr'].range('A2').value==None:
    not_write_EngGeo = 0

if wbxl.sheets['Parametr'].range('A3').value=='+':
    not_write_EngGeo_not_EngGeo_parametr = 1
if wbxl.sheets['Parametr'].range('A3').value==None:
    not_write_EngGeo_not_EngGeo_parametr = 0

if wbxl.sheets['Parametr'].range('A4').value=='+':
    write_and_createISP = 1
if wbxl.sheets['Parametr'].range('A4').value==None:
    write_and_createISP = 0

INT_or_STR = wbxl.sheets['Parametr'].range('A6').value

try:
    r = 2
    r = str(r)
    jit(parallel=True)
    while wbxl.sheets['Start'].range('G' + r).value == '#':
        os.chdir(File_Path)
        if INT_or_STR == 0:
            LAB_NO = str(wbxl.sheets['Start'].range('H' + r).value)
        else:
            LAB_NO = int(wbxl.sheets['Start'].range('H' + r).value)
            LAB_NO = str(LAB_NO)

        if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
            os.mkdir(LAB_NO)

        TPS = wbxl.sheets['Start'].range('A' + r).value
        TPD = wbxl.sheets['Start'].range('B' + r).value
        SPS = wbxl.sheets['Start'].range('C' + r).value
        SPD = wbxl.sheets['Start'].range('D' + r).value
        TPDL = wbxl.sheets['Start'].range('E' + r).value
        SPDL = wbxl.sheets['Start'].range('F' + r).value

        C = wbxl.sheets['Start'].range('K' + r).value
        F = wbxl.sheets['Start'].range('L' + r).value
        E = wbxl.sheets['Start'].range('M' + r).value

        Grunt = wbxl.sheets['Start'].range('I' + r).value

        DOP = wbxl.sheets['Start'].range('O' + r).value
        GLUB_DOP = wbxl.sheets['Start'].range('P' + r).value
        DOPplus = wbxl.sheets['Start'].range('Q' + r).value

        conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + (PUTIN) + '')
        cursor = conn.cursor()
        crsr = conn.cursor()

        cursor.execute(
            "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
        for row in cursor.fetchall():
            PROBEGR_IDS = (row.OBJID)
            GLUB = (row.GLUB_OT)
        cursor.execute(
            "SELECT (OBJID),(PROBAGR_OBJID) FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                'PROBAGR_OBJID': PROBEGR_IDS})
        for row in cursor.fetchall():
            PROBEGR_SVODKA = (row.OBJID)
        cursor.execute(
            "SELECT (OBJID),(Ip),(IL),(Sr),(Kpor),(Ro) FROM SVODKA_FIZMEX WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                'PROBEGR_SVODKA': PROBEGR_SVODKA})
        for row in cursor.fetchall():
            Ip = (row.Ip)
            IL = (row.IL)
            Sr = (row.Sr)
            Kpor = (row.Kpor)
            Ro = (row.Ro)

        # генератор
        CM3DATA_OBJID = (''.join([random.choice(list('1234567890ABCDEF'))
                                  for x in range(32)]))
        if (write_and_createISP == 1 or not_create_ISP == 1) and (TPS == '+' or TPD == '+' or TPDL == '+'):  # TPDL
            crsr.execute(
                "INSERT INTO CM3OPR (OBJID,	PROBEGR_ID,	DATE_TEST,	SCHEMA,	STOCK_AREA,	AREA,	HEIGHT,	ZOOM_PERCENT,	PRIBOR_OBJID) "
                "VALUES ('%(OBJID)s',	'%(PROBEGR_ID2)s',	'%(DATE_TEST)s',	'%(SCHEMA)s',	'%(STOCK_AREA)s',	'1134,115',	'%(HEIGHT)s',	'%(ZOOM_PERCENT)s',	'F70EC2ACDCCA4FB19C2C16C0DAD8CD38')"
                % {'OBJID': CM3DATA_OBJID, 'PROBEGR_ID2': PROBEGR_IDS, 'DATE_TEST': directory_time, 'SCHEMA': 2,
                   'STOCK_AREA': -777777, 'HEIGHT': 76, 'ZOOM_PERCENT': 100})

        if TPS == '+':  # TPS
            Kgrap = randint(-3, -2) / 10  # коэффициент для изменения вида графиков
            N = 2 * math.tan(math.pi * F / 180) * ((((math.tan(math.pi * F / 180)) ** 2) + 1) ** (1 / 2)) + 2 * (
                    (math.tan(math.pi * F / 180)) ** 2) + 1
            M = 2 * (N ** (1 / 2)) * C
            # расчет давления исходя из типа грунта
            if DOP == '+':
                Press1 = (((GLUB * 20 + DOPplus) / 2) / 2) / 1000
                Press2 = ((GLUB * 20 + DOPplus) / 2) / 1000
                Press3 = (GLUB * 20 + DOPplus) / 1000
            elif Ip == None:
                Kgrap = randint(-3, -2) / 10  # коэффициент для изменения вида графиков
                cursor.execute(
                    "SELECT (OBJID),(GGR10),(G10_5),(G5_2),(G2_1),(G1_05),(G05_025),(G025_01),(G01_005) FROM SVODKA_GRANS WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                        'PROBEGR_SVODKA': PROBEGR_SVODKA})
                for row in cursor.fetchall():
                    if row.GGR10 == None:
                        GGR10 = 0
                    else:
                        GGR10 = float(row.GGR10)
                    if row.G10_5 == None:
                        G10_5 = 0
                    else:
                        G10_5 = float(row.G10_5)
                    if row.G5_2 == None:
                        G5_2 = 0
                    else:
                        G5_2 = float(row.G5_2)
                    if row.G2_1 == None:
                        G2_1 = 0
                    else:
                        G2_1 = float(row.G2_1)
                    if row.G1_05 == None:
                        G1_05 = 0
                    else:
                        G1_05 = float(row.G1_05)
                    if row.G05_025 == None:
                        G05_025 = 0
                    else:
                        G05_025 = float(row.G05_025)
                    if row.G025_01 == None:
                        G025_01 = 0
                    else:
                        G025_01 = float(row.G025_01)
                    if row.G01_005 == None:
                        G01_005 = 0
                    else:
                        G01_005 = float(row.G01_005)
                    # гравелистые                   крупные                              средние плотные
                if (G5_2 + G10_5 + GGR10) > 25 or (G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50 or (
                        (G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50 and Kpor <= 0.55):
                    Press1 = 0.100
                    Press2 = 0.300
                    Press3 = 0.500
                    # средние средней плотности
                elif ((G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50 and (0.55 < Kpor and Kpor <= 0.7)):
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                    #  мелкие плотные
                elif ((G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75 and (Kpor <= 0.6)):
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                    # мелкиеи средней плотности
                elif (((G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75) and (0.6 < Kpor <= 0.75)):
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                    # средние рыхлые                                    мелкие рыхлые                                                     пылеватые
                elif ((G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50 and Kpor > 0.7) or (
                        (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75 and Kpor > 0.75) or (
                        (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) < 75):
                    Press1 = 0.1
                    Press2 = 0.150
                    Press3 = 0.200
            else:
                Ip = float(Ip)
                IL = float(IL)
                if Ip <= 7 and IL <= 0.5:
                    Kgrap = randint(-2, -1) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                if Ip <= 7 and IL > 0.5:
                    Kgrap = randint(-2, -1) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.150
                    Press3 = 0.200
                if Ip > 7 and Ip < 17 and IL <= 0.5:
                    Kgrap = randint(-1, 1) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                if Ip > 7 and Ip < 17 and IL > 0.5:
                    Kgrap = randint(-1, 1) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.150
                    Press3 = 0.200
                if Ip >= 17 and IL <= 0.25:
                    Kgrap = randint(1, 2) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.300
                    Press3 = 0.500
                if Ip >= 17 and IL > 0.25 and IL <= 0.5:
                    Kgrap = randint(1, 2) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.200
                    Press3 = 0.300
                if Ip >= 17 and IL > 0.5:
                    Kgrap = randint(1, 2) / 10  # коэффициент для изменения вида графиков
                    Press1 = 0.100
                    Press2 = 0.150
                    Press3 = 0.200
            st1 = (Press1 * N + M)
            st3 = (Press3 * N + M)
            st2 = (((st1 + st3) / 2) * (Press2 / ((Press3 + Press1) / 2)))

            # 1 давление
            df_Press1=[Press1]
            df_Press1=pd.DataFrame(df_Press1)

            df_st1 = [st1]
            df_st1 = pd.DataFrame(df_st1)

            # 2 давление
            df_Press2 = [Press2]
            df_Press2 = pd.DataFrame(df_Press2)

            df_st2 = [st2]
            df_st2 = pd.DataFrame(df_st2)

            # 3 давление
            df_Press3 = [Press3]
            df_Press3 = pd.DataFrame(df_Press3)

            df_st3 = [st3]
            df_st3 = pd.DataFrame(df_st3)

            df_Kgrap = [Kgrap]
            df_Kgrap = pd.DataFrame(df_Kgrap)

            df_CM3DATA_OBJID = [CM3DATA_OBJID]
            df_CM3DATA_OBJID = pd.DataFrame(df_CM3DATA_OBJID)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/TPS.xlsx', mode='a', engine="openpyxl",if_sheet_exists='overlay')
            # 1 давление
            df_Press1.to_excel(writer, sheet_name='100', startcol=11, startrow=1, index=False, index_label=False,
                               header=False)
            df_st1.to_excel(writer, sheet_name='100', startcol=12, startrow=38, index=False, index_label=False,
                               header=False)
            df_Kgrap.to_excel(writer, sheet_name='Расчет100', startcol=4, startrow=0, index=False, index_label=False,
                            header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_CM3DATA_OBJID.to_excel(writer, sheet_name='EngGeo100', startcol=1, startrow=0, index=False, index_label=False,
                              header=False)
            # 2 давление
            df_Press2.to_excel(writer, sheet_name='200', startcol=11, startrow=1, index=False, index_label=False,
                               header=False)
            df_st2.to_excel(writer, sheet_name='200', startcol=12, startrow=38, index=False, index_label=False,
                            header=False)
            df_Kgrap.to_excel(writer, sheet_name='Расчет200', startcol=4, startrow=0, index=False, index_label=False,
                              header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_CM3DATA_OBJID.to_excel(writer, sheet_name='EngGeo200', startcol=1, startrow=0, index=False,
                                          index_label=False,
                                          header=False)
            # 3 давление
            df_Press3.to_excel(writer, sheet_name='300', startcol=11, startrow=1, index=False, index_label=False,
                               header=False)
            df_st3.to_excel(writer, sheet_name='300', startcol=12, startrow=38, index=False, index_label=False,
                            header=False)
            df_Kgrap.to_excel(writer, sheet_name='Расчет300', startcol=4, startrow=0, index=False, index_label=False,
                              header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_CM3DATA_OBJID.to_excel(writer, sheet_name='EngGeo300', startcol=1, startrow=0, index=False,
                                          index_label=False,
                                          header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/TPS.xlsx')
            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispTPS():

                    data_excel = xw.sheets('100')
                    # 1 давление
                    df1 = data_excel.range('A1:N39').options(pd.DataFrame, header=1, index_col=0).value
                    df1.to_csv('Z:/Zapis/ISP/Stan/Test.1.log', sep='\t')  # создание лога из выведенного датафрейма
                    data_excel = xw.sheets('200')
                    # 2 давление
                    df1 = data_excel.range('A1:N39').options(pd.DataFrame, header=1, index_col=0).value
                    df1.to_csv('Z:/Zapis/ISP/Stan/Test.2.log', sep='\t')  # создание лога из выведенного датафрейма
                    data_excel = xw.sheets('300')
                    # 3 давление
                    df1 = data_excel.range('A1:N39').options(pd.DataFrame, header=1, index_col=0).value
                    df1.to_csv('Z:/Zapis/ISP/Stan/Test.3.log', sep='\t')  # создание лога из выведенного датафрейма

                    Press11 = str(Press1)  # перевод давления в строку для того, чтобы ее воспринимал модуль OS
                    Press21 = str(Press2)
                    Press31 = str(Press3)
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('TPS')
                    os.chdir(File_Path + LAB_NO + '/TPS/')
                    os.mkdir(Press11)
                    os.chdir(Press11)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/TPS/' + Press11)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '76	38')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.1.log', File_Path + LAB_NO + '/TPS/' + Press11 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.mkdir(Press21)
                    os.chdir(Press21)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/TPS/' + Press21)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '76	38')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.2.log', File_Path + LAB_NO + '/TPS/' + Press21 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.mkdir(Press31)
                    os.chdir(Press31)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/TPS/' + Press31)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '76	38')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.3.log', File_Path + LAB_NO + '/TPS/' + Press31 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.chdir('..')
                    os.chdir('..')
                    return create_base_ispTPS
                create_base_ispTPS()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_TPS():
                    GLUB1 = str(Press1).replace('.', ',')
                    GLUB2 = str(Press2).replace('.', ',')
                    GLUB3 = str(Press3).replace('.', ',')

                    crsr.execute(
                        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
                        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
                        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 1, 'UNIFORM_PRESSURE': GLUB1, 'FROM_MORECULON': -1,
                           'FROM_NU_E': 0})

                    crsr.execute(
                        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
                        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
                        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 2, 'UNIFORM_PRESSURE': GLUB2, 'FROM_MORECULON': -1,
                           'FROM_NU_E': 0})
                    crsr.execute(
                        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
                        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
                        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 3, 'UNIFORM_PRESSURE': GLUB3, 'FROM_MORECULON': -1,
                           'FROM_NU_E': 0})

                    data_excel = xw.sheets('EngGeo100')
                    df1 = (data_excel.range('A1:J39').options(pd.DataFrame, header=1, index_col=0).value)

                    data_excel2 = xw.sheets('EngGeo200')
                    df2 = (data_excel2.range('A1:J39').options(pd.DataFrame, header=1, index_col=0).value)

                    data_excel3 = xw.sheets('EngGeo300')
                    df3 = (data_excel3.range('A1:J39').options(pd.DataFrame, header=1, index_col=0).value)
                    for u in range(0, 38):
                        crsr.execute(
                            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                            % {'OBJID': (str(df1.iloc[int(u), 0])),
                               'EXAM_NUM': ((str(df1.iloc[int(u), 1])).replace('.', ',')),
                               'FORCE': (str(df1.iloc[int(u), 2])).replace('.', ','),
                               'DEFORM': (str(df1.iloc[int(u), 3])).replace('.', ','),
                               'DEFORM_VOL': (str(df1.iloc[int(u), 4])).replace('.', ','),
                               'SERIAL_NUM': (str(df1.iloc[int(u), 6])).replace('.', ','),
                               'SELECTED': (str(df1.iloc[int(u), 5])).replace('.', ','),
                               'SEL_FOR_NU': (str(df1.iloc[int(u), 8])).replace('.', ',')})
                        crsr.execute(
                            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                            % {'OBJID': (str(df2.iloc[int(u), 0])),
                               'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                               'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                               'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                               'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                               'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                               'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                               'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                        crsr.execute(
                            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                            % {'OBJID': (str(df3.iloc[int(u), 0])),
                               'EXAM_NUM': ((str(df3.iloc[int(u), 1])).replace('.', ',')),
                               'FORCE': (str(df3.iloc[int(u), 2])).replace('.', ','),
                               'DEFORM': (str(df3.iloc[int(u), 3])).replace('.', ','),
                               'DEFORM_VOL': (str(df3.iloc[int(u), 4])).replace('.', ','),
                               'SERIAL_NUM': (str(df3.iloc[int(u), 6])).replace('.', ','),
                               'SELECTED': (str(df3.iloc[int(u), 5])).replace('.', ','),
                               'SEL_FOR_NU': (str(df3.iloc[int(u), 8])).replace('.', ',')})
                        u += 1

                    crsr.commit()
                    return write_EngGeo_TPS

                write_EngGeo_TPS()
            app.kill()

        # Деформация
        if TPD == '+':  # TPD
            cursor.execute(
                "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
            for row in cursor.fetchall():
                GLUB = (row.GLUB_OT)
            if Ip == None:
                KfPUS = randint(120, 130)
                Kgrap = randint(-50, -30) / 1000
                K_0 = 0.5
            else:
                Ip = float(Ip)
                IL = float(IL)
                if Ip <= 7 and IL > 0.5:
                    KfPUS = randint(120, 130)
                    Kgrap = randint(-30, 0) / 1000
                    K_0 = 1
                if Ip <= 7 and IL <= 0.5:
                    KfPUS = randint(120, 130)
                    Kgrap = randint(-30, 0) / 1000
                    K_0 = 0.7
                if Ip > 7 and Ip < 17 and IL <= 0.5:
                    KfPUS = randint(44, 60)
                    Kgrap = randint(0, 30) / 1000
                    K_0 = 0.7
                if Ip > 7 and Ip < 17 and IL > 0.5:
                    KfPUS = randint(44, 60)
                    Kgrap = randint(0, 30) / 1000
                    K_0 = 1
                if Ip >= 17 and IL <= 0.5:
                    KfPUS = randint(80, 92)
                    Kgrap = randint(30, 60) / 1000
                    K_0 = 0.7
                if Ip >= 17 and IL > 0.5:
                    KfPUS = randint(80, 92)
                    Kgrap = randint(30, 60) / 1000
                    K_0 = 1

            df_KfPUS = [KfPUS]
            df_KfPUS = pd.DataFrame(df_KfPUS)

            df_PressD = [((GLUB * 20) / 1000) * K_0]
            df_PressD = pd.DataFrame(df_PressD)

            df_E = [E]
            df_E = pd.DataFrame(df_E)

            df_Kgrap = [Kgrap]
            df_Kgrap = pd.DataFrame(df_Kgrap)

            df_CM3DATA_OBJID = [CM3DATA_OBJID]
            df_CM3DATA_OBJID = pd.DataFrame(df_CM3DATA_OBJID)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/TPD.xlsx', mode='a', engine="openpyxl",
                                    if_sheet_exists='overlay')

            df_KfPUS.to_excel(writer, sheet_name='Расчет', startcol=6, startrow=0, index=False,
                               index_label=False,
                               header=False)

            df_PressD.to_excel(writer, sheet_name='TPD', startcol=11, startrow=1, index=False, index_label=False,
                            header=False)

            df_E.to_excel(writer, sheet_name='TPD', startcol=20, startrow=8, index=False,
                              index_label=False,
                              header=False)

            df_Kgrap.to_excel(writer, sheet_name='TPD', startcol=24, startrow=0, index=False,
                              index_label=False,
                              header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_CM3DATA_OBJID.to_excel(writer, sheet_name='EngGeo', startcol=1, startrow=0, index=False,
                                          index_label=False,
                                          header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/TPD.xlsx')

            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispTPD():

                    data_excel = xw.sheets('TPD')
                    dfD = data_excel.range('A1:N39').options(pd.DataFrame, header=1, index_col=0).value
                    dfD.to_csv('Z:/Zapis/ISP/Stan/Test.D.log', sep='\t')  # создание лога из выведенного датафрейма
                    PressD = str(GLUB * 20)  # перевод давления в строку для того, чтобы ее воспринимал модуль OS
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path)
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('TPD')
                    os.chdir(File_Path + LAB_NO + '/TPD/')
                    os.mkdir(PressD)
                    os.chdir(PressD)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/TPD/' + PressD)
                    os.mkdir('General')

                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '76	38')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.D.log', File_Path + LAB_NO + '/TPD/' + PressD + '/Test')
                    return create_base_ispTPD

                create_base_ispTPD()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_TPD():
                    GLUB1 = str((GLUB * 20 / 1000) * 0.7).replace('.', ',')
                    crsr.execute(
                        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
                        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
                        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 0, 'UNIFORM_PRESSURE': GLUB1, 'FROM_MORECULON': 0,
                           'FROM_NU_E': -1, })
                    data_excel = xw.sheets('EngGeo')
                    df2 = (data_excel.range('A1:J39').options(pd.DataFrame, header=1, index_col=0).value)
                    for u in range(0, 38):
                        crsr.execute(
                            "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                            "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                            % {'OBJID': (str(df2.iloc[int(u), 0])),
                               'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                               'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                               'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                               'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                               'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                               'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                               'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                        u += 1
                    crsr.commit()
                    return write_EngGeo_TPD

                write_EngGeo_TPD()

            app.kill()

        # tpdl
        if TPDL == '+':  # TPDL
            cursor.execute(
                "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
            for row in cursor.fetchall():
                GLUB = (row.GLUB_OT)
            if Ip == None:
                KfPUS = randint(25, 27)
                KfPUS1 = randint(25, 27)
                TOCHKA = 1.6
                K_0 = 0.5
            else:
                Ip = float(Ip)
                IL = float(IL)
                if Ip <= 7 and IL > 0.5:
                    KfPUS = randint(37, 40)
                    KfPUS1 = randint(37, 40)
                    TOCHKA = 1.5
                    K_0 = 1
                if Ip <= 7 and IL <= 0.5:
                    KfPUS = randint(37, 40)
                    KfPUS1 = randint(37, 40)
                    TOCHKA = 1.5
                    K_0 = 0.7
                if Ip > 7 and Ip < 17 and IL <= 0.5:
                    KfPUS = randint(49, 51)
                    KfPUS1 = randint(49, 51)
                    TOCHKA = 1.3
                    K_0 = 0.7
                if Ip > 7 and Ip < 17 and IL > 0.5:
                    KfPUS = randint(49, 51)
                    KfPUS1 = randint(49, 51)
                    TOCHKA = 1.23
                    K_0 = 1
                if Ip >= 17 and IL <= 0.5:
                    KfPUS = randint(43, 45)
                    KfPUS1 = randint(43, 45)
                    TOCHKA = 1.21
                    K_0 = 0.7
                if Ip >= 17 and IL > 0.5:
                    KfPUS = randint(43, 45)
                    KfPUS1 = randint(43, 45)
                    TOCHKA = 1.15
                    K_0 = 1

            df_KfPUS = [KfPUS]
            df_KfPUS = pd.DataFrame(df_KfPUS)

            df_KfPUS1 = [KfPUS1]
            df_KfPUS1 = pd.DataFrame(df_KfPUS1)

            df_PressD = [((GLUB * 20) / 1000) * K_0]
            df_PressD = pd.DataFrame(df_PressD)

            df_E = [E]
            df_E = pd.DataFrame(df_E)

            df_CM3DATA_OBJID = [CM3DATA_OBJID]
            df_CM3DATA_OBJID = pd.DataFrame(df_CM3DATA_OBJID)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/TPDS.xlsx', mode='a', engine="openpyxl",
                                    if_sheet_exists='overlay')

            df_KfPUS.to_excel(writer, sheet_name='Расчет', startcol=6, startrow=0, index=False,
                              index_label=False,
                              header=False)

            df_KfPUS1.to_excel(writer, sheet_name='Расчет', startcol=6, startrow=18, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.15:
                df_PressD.to_excel(writer, sheet_name='TPDL1.15', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.15', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.21:
                df_PressD.to_excel(writer, sheet_name='TPDL1.21', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.21', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.23:
                df_PressD.to_excel(writer, sheet_name='TPDL1.23', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.23', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.3:
                df_PressD.to_excel(writer, sheet_name='TPDL1.3', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.3', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.5:
                df_PressD.to_excel(writer, sheet_name='TPDL1.5', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.5', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)
            if TOCHKA == 1.6:
                df_PressD.to_excel(writer, sheet_name='TPDL1.6', startcol=11, startrow=1, index=False, index_label=False,
                                   header=False)

                df_E.to_excel(writer, sheet_name='TPDL1.6', startcol=21, startrow=7, index=False,
                              index_label=False,
                              header=False)

            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_CM3DATA_OBJID.to_excel(writer, sheet_name='EngGeo', startcol=1, startrow=0, index=False,
                                          index_label=False,
                                          header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/TPDS.xlsx')

            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispTPDL():
                    LAB_NO1 = str(LAB_NO)
                    if TOCHKA == 1.6:
                        data_excel = xw.sheets['TPDL1.6']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if TOCHKA == 1.5:
                        data_excel = xw.sheets['TPDL1.5']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if TOCHKA == 1.3:
                        data_excel = xw.sheets['TPDL1.3']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if TOCHKA == 1.23:
                        data_excel = xw.sheets['TPDL1.23']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if TOCHKA == 1.21:
                        data_excel = xw.sheets['TPDL1.21']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if TOCHKA == 1.15:
                        data_excel = xw.sheets['TPDL1.15']
                        dfDL = data_excel.range('A1:N64').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.DL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    PressD = str(
                        (GLUB * 20) / 1000)  # перевод давления в строку для того, чтобы ее воспринимал модуль OS
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path)
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('TPDL')
                    os.chdir(File_Path + LAB_NO + '/TPDL/')
                    os.mkdir(PressD)
                    os.chdir(PressD)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/TPDL/' + PressD)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '76	38')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.DL.log', File_Path + LAB_NO + '/TPDL/' + PressD + '/Test')
                    return create_base_ispTPDL

                create_base_ispTPDL()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_TPDL():
                    GLUB1 = str((GLUB * 20 / 1000)*0.7).replace('.', ',')
                    crsr = conn.cursor()
                    crsr.execute(
                        "INSERT INTO CM3EXAM (OBJID,	EXAM_NUM,	UNIFORM_PRESSURE,	FROM_MORECULON,	FROM_NU_E,	AREA,HEIGHT,	STR_OBJID, REGIME) "
                        "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(UNIFORM_PRESSURE)s',	'%(FROM_MORECULON)s',	'%(FROM_NU_E)s',	'1134,115', '76',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0','1')"
                        % {'OBJID': CM3DATA_OBJID, 'EXAM_NUM': 4, 'UNIFORM_PRESSURE': GLUB1, 'FROM_MORECULON': 0,
                           'FROM_NU_E': -1, })

                    data_excel = xw.sheets('EngGeo')
                    if TOCHKA == 1.6:
                        df2 = (data_excel.range('BD1:BM64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()

                    if TOCHKA == 1.5:
                        df2 = (data_excel.range('AS1:BB64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()

                    if TOCHKA == 1.3:
                        df2 = (data_excel.range('AH1:AQ64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()
                    if TOCHKA == 1.23:
                        df2 = (data_excel.range('W1:AF64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()
                    if TOCHKA == 1.21:
                        df2 = (data_excel.range('L1:U64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()
                    if TOCHKA == 1.15:
                        df2 = (data_excel.range('A1:J64').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 63):
                            crsr.execute(
                                "INSERT INTO CM3DATA (OBJID,EXAM_NUM,FORCE,DEFORM,DEFORM_VOL,SELECTED,SERIAL_NUM,SEL_FOR_NU) "
                                "VALUES ('%(OBJID)s',	'%(EXAM_NUM)s',	'%(FORCE)s',	'%(DEFORM)s',	'%(DEFORM_VOL)s','%(SELECTED)s',	'%(SERIAL_NUM)s','%(SEL_FOR_NU)s')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'EXAM_NUM': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'FORCE': (str(df2.iloc[int(u), 2])).replace('.', ','),
                                   'DEFORM': (str(df2.iloc[int(u), 3])).replace('.', ','),
                                   'DEFORM_VOL': (str(df2.iloc[int(u), 4])).replace('.', ','),
                                   'SERIAL_NUM': (str(df2.iloc[int(u), 6])).replace('.', ','),
                                   'SELECTED': (str(df2.iloc[int(u), 5])).replace('.', ','),
                                   'SEL_FOR_NU': (str(df2.iloc[int(u), 8])).replace('.', ',')})
                            u += 1

                        else:
                            crsr.commit()

                    return write_EngGeo_TPDL

                write_EngGeo_TPDL()

            app.kill()

        # одноплоскостной срез
        if SPS == '+':  # SPS

            # генератор
            SDDATA_OBJID = (''.join([random.choice(list('1234567890ABCDEF'))
                                     for x in range(32)]))

            cursor.execute(
                "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
            for row in cursor.fetchall():
                PROBEGR_IDS = (row.OBJID)
                GLUB = (row.GLUB_OT)
            cursor.execute(
                "SELECT (OBJID),(PROBAGR_OBJID) FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                    'PROBAGR_OBJID': PROBEGR_IDS})
            for row in cursor.fetchall():
                PROBEGR_SVODKA = (row.OBJID)
            cursor.execute(
                "SELECT (OBJID),(Ip),(IL),(Sr) FROM SVODKA_FIZMEX WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                    'PROBEGR_SVODKA': PROBEGR_SVODKA})
            for row in cursor.fetchall():
                Ip = (row.Ip)
                IL = (row.IL)
                Sr = (row.Sr)
            Rad = (F * math.pi) / 180
            # расчет давления исходя из типа грунта
            if DOP == '+':
                Press1 = (((GLUB * 20 + DOPplus) / 2) / 2) / 1000
                Press2 = ((GLUB * 20 + DOPplus) / 2) / 1000
                Press3 = (GLUB * 20 + DOPplus) / 1000
            else:
                if Ip == None:
                    KfPUS = randint(120, 130)
                else:
                    Ip = float(Ip)
                    IL = float(IL)
                    if Ip <= 7 and IL <= 0.5:
                        Press1 = 0.100
                        Press2 = 0.200
                        Press3 = 0.300
                    if Ip <= 7 and IL > 0.5:
                        Press1 = 0.100
                        Press2 = 0.150
                        Press3 = 0.200
                    if Ip > 7 and Ip < 17 and IL <= 0.5:
                        Press1 = 0.100
                        Press2 = 0.200
                        Press3 = 0.300
                    if Ip > 7 and Ip < 17 and IL > 0.5:
                        Press1 = 0.100
                        Press2 = 0.150
                        Press3 = 0.200
                    if Ip >= 17 and IL <= 0.25:
                        Press1 = 0.100
                        Press2 = 0.300
                        Press3 = 0.500
                    if Ip >= 17 and IL > 0.25 and IL <= 0.5:
                        Press1 = 0.100
                        Press2 = 0.200
                        Press3 = 0.300
                    if Ip >= 17 and IL > 0.5:
                        Press1 = 0.100
                        Press2 = 0.150
                        Press3 = 0.200
            st1 = (Press1 * math.tan(Rad) + C)
            st3 = (Press3 * math.tan(Rad) + C)
            st2 = (((st1 + st3) / 2) * (Press2 / ((Press3 + Press1) / 2)))

            df_Press1 = [Press1]
            df_Press1 = pd.DataFrame(df_Press1)

            df_Press2 = [Press2]
            df_Press2 = pd.DataFrame(df_Press2)

            df_Press3 = [Press3]
            df_Press3 = pd.DataFrame(df_Press3)

            df_F = [F]
            df_F = pd.DataFrame(df_F)

            df_C = [C]
            df_C = pd.DataFrame(df_C)

            df_st1 = [st1]
            df_st1 = pd.DataFrame(df_st1)

            df_st2 = [st2]
            df_st2 = pd.DataFrame(df_st2)

            df_st3 = [st3]
            df_st3 = pd.DataFrame(df_st3)

            df_SDDATA_OBJID = [SDDATA_OBJID]
            df_SDDATA_OBJID = pd.DataFrame(df_SDDATA_OBJID)

            num_sps1 = randint(15, 19)

            num_sps2 = randint(16, 19)

            num_sps3 = randint(15, 19)

            writer= pd.ExcelWriter('Z:/Zapis/ISP/Grapics/SPS.xlsx', mode='a', engine='openpyxl',if_sheet_exists='overlay')

            df_Press1.to_excel(writer, sheet_name='срезы', startrow=24,startcol=1, index=False, index_label=False,header=False)
            df_Press2.to_excel(writer, sheet_name='срезы', startrow=24, startcol=2, index=False, index_label=False,header=False)
            df_Press3.to_excel(writer, sheet_name='срезы', startrow=24, startcol=3, index=False, index_label=False,header=False)
            df_F.to_excel(writer, sheet_name='срезы', startrow=27, startcol=5, index=False, index_label=False,header=False)
            df_C.to_excel(writer, sheet_name='срезы', startrow=28, startcol=5, index=False, index_label=False,header=False)

            df_st1.to_excel(writer, sheet_name='срезы', startrow=num_sps1-1, startcol=22, index=False, index_label=False,header=False)
            df_st2.to_excel(writer, sheet_name='срезы', startrow=num_sps2-1, startcol=27, index=False, index_label=False,header=False)
            df_st3.to_excel(writer, sheet_name='срезы', startrow=num_sps3-1, startcol=32, index=False, index_label=False,header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_SDDATA_OBJID.to_excel(writer, sheet_name='EngGeo', startrow=2, startcol=2, index=False, index_label=False,header=False)

            writer.save()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/SPS.xlsx')
            data_excel = xw.sheets['срезы']
            st01 = data_excel.range('V7:W8').options(pd.DataFrame).value
            st01 = (st01.iat[0, 0])
            st02 = data_excel.range('AA7:AB8').options(pd.DataFrame).value
            st02 = (st02.iat[0, 0])
            st03 = data_excel.range('AF7:AG8').options(pd.DataFrame).value
            st03 = (st03.iat[0 ,0])

            app.kill()

            num_sps1 = int(num_sps1)
            range_st1 = (st1 - st01) / (num_sps1 - 8)

            num_sps2 = int(num_sps2)
            range_st2 = (st2 - st02) / (num_sps2 - 8)

            num_sps3 = int(num_sps3)
            range_st3 = (st3 - st03) / (num_sps3 - 8)

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/SPS.xlsx')
            data_excel = xw.sheets['срезы']

            # 1 press
            kg_sps = 9
            kf_end = 21

            KFumn1 = 1
            KFumn2 = 1
            KFumn3 = 1

            num_sps1end = num_sps1 + 1
            num_sps1end = str(num_sps1end)
            kfmum_sps1 = data_excel.range('W' + num_sps1end).options(pd.DataFrame, header=1, index_col=0).value
            KFdel1 = 2
            num_sps1end = int(num_sps1end)

            # 2 press

            num_sps2end = num_sps2 + 1
            num_sps2end = str(num_sps2end)
            kfmum_sps2 = data_excel.range('AB' + num_sps2end).options(pd.DataFrame, header=1, index_col=0).value
            KFdel2 = 2
            num_sps2end = int(num_sps2end)

            # 3 press
            num_sps3end = num_sps3 + 1
            num_sps3end = str(num_sps3end)
            kfmum_sps3 = data_excel.range('AG' + num_sps3end).options(pd.DataFrame, header=1, index_col=0).value
            KFdel3 = 2
            num_sps3end = int(num_sps3end)

            app.kill()

            # 1 давление до макс точки
            df_kfsps=[]
            kfsps=0

            for kfsps in range(kg_sps, num_sps1):
                kfsps_insert = st01 + range_st1 * KFumn1
                df_kfsps.insert(kfsps,[kfsps_insert])
                KFumn1 += 1
                kfsps += 1

            df_kfsps = pd.DataFrame(df_kfsps)

            # 1 давление после макс точки
            df_kfmum_sps1 = []
            kfsps = 0

            for kfsps in range(num_sps1end, kf_end):
                kfsps_insert = st1 - 0.001 * KFdel1
                df_kfmum_sps1.insert(kfsps, [kfsps_insert])
                kfsps += 1
                KFdel1 += 1
            df_kfmum_sps1 = pd.DataFrame(df_kfmum_sps1)

            # 2 давление до макс точки
            df_kfsps2 = []
            kfsps = 0

            for kfsps in range(kg_sps, num_sps2):
                kfsps_insert = st02 + range_st2 * KFumn2
                df_kfsps2.insert(kfsps, [kfsps_insert])
                KFumn2 += 1
                kfsps += 1

            df_kfsps2 = pd.DataFrame(df_kfsps2)

            # 2 давление после макс точки
            df_kfmum_sps2 = []
            kfsps = 0

            for kfsps in range(num_sps2end, kf_end):
                kfsps_insert = st2 - 0.001 * KFdel2
                df_kfmum_sps2.insert(kfsps, [kfsps_insert])
                kfsps += 1
                KFdel2 += 1
            df_kfmum_sps2 = pd.DataFrame(df_kfmum_sps2)

            # 3 давление до макс точки
            df_kfsps3 = []
            kfsps = 0

            for kfsps in range(kg_sps, num_sps3):
                kfsps_insert = st03 + range_st3 * KFumn3
                df_kfsps3.insert(kfsps, [kfsps_insert])
                KFumn3 += 1
                kfsps += 1

            df_kfsps3 = pd.DataFrame(df_kfsps3)

            # 3 давление после макс точки
            df_kfmum_sps3 = []
            kfsps = 0

            for kfsps in range(num_sps3end, kf_end):
                kfsps_insert = st3 - 0.001 * KFdel3
                df_kfmum_sps3.insert(kfsps, [kfsps_insert])
                kfsps += 1
                KFdel3 += 1
            df_kfmum_sps3 = pd.DataFrame(df_kfmum_sps3)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/SPS.xlsx', mode='a', engine='openpyxl',
                                    if_sheet_exists='overlay')
            # 1 давление
            df_kfsps.to_excel(writer, sheet_name='срезы', startcol=22, startrow=8, index=False,
                              index_label=False,
                              header=False)
            df_kfmum_sps1.to_excel(writer, sheet_name='срезы', startcol=22, startrow=num_sps1end-1, index=False,
                              index_label=False,
                              header=False)
            # 2 давление
            df_kfsps2.to_excel(writer, sheet_name='срезы', startcol=27, startrow=8, index=False,
                              index_label=False,
                              header=False)
            df_kfmum_sps2.to_excel(writer, sheet_name='срезы', startcol=27, startrow=num_sps2end - 1, index=False,
                                   index_label=False,
                                   header=False)
            # 3 давление
            df_kfsps3.to_excel(writer, sheet_name='срезы', startcol=32, startrow=8, index=False,
                               index_label=False,
                               header=False)
            df_kfmum_sps3.to_excel(writer, sheet_name='срезы', startcol=32, startrow=num_sps3end - 1, index=False,
                                   index_label=False,
                                   header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/SPS.xlsx')

            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispSPS():

                    data_excel = xw.sheets('На выгрузку срезы')

                    df1 = data_excel.range('C2:L16').options(pd.DataFrame, header=1, index_col=0).value
                    df2 = data_excel.range('P2:Y16').options(pd.DataFrame, header=1, index_col=0).value
                    df3 = data_excel.range('I21:R35').options(pd.DataFrame, header=1, index_col=0).value

                    df1.to_csv('Z:/Zapis/ISP/Stan/Test.1.log', sep='\t',
                               encoding="ANSI")  # создание лога из выведенного датафрейма
                    df2.to_csv('Z:/Zapis/ISP/Stan/Test.2.log', sep='\t',
                               encoding="ANSI")  # создание лога из выведенного датафрейма
                    df3.to_csv('Z:/Zapis/ISP/Stan/Test.3.log', sep='\t',
                               encoding="ANSI")  # создание лога из выведенного датафрейма

                    Press11 = str(Press1)  # перевод давления в строку для того, чтобы ее воспринимал модуль OS
                    Press21 = str(Press2)
                    Press31 = str(Press3)
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path)
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('SPS')
                    os.chdir(File_Path + LAB_NO + '/SPS/')
                    os.mkdir(Press11)
                    os.chdir(Press11)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/SPS/' + Press11)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '35	71.5')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.1.log', File_Path + LAB_NO + '/SPS/' + Press11 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.mkdir(Press21)
                    os.chdir(Press21)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/SPS/' + Press21)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '35	71.5')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.2.log', File_Path + LAB_NO + '/SPS/' + Press21 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.mkdir(Press31)
                    os.chdir(Press31)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/SPS/' + Press31)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '35	71.5')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.3.log', File_Path + LAB_NO + '/SPS/' + Press31 + '/Test')
                    os.chdir('..')
                    os.chdir('..')
                    os.chdir('..')
                    os.chdir('..')
                    return create_base_ispSPS

                create_base_ispSPS()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_SPS():
                    st1s = str(st1).replace('.', ',')
                    st2s = str(st2).replace('.', ',')
                    st3s = str(st3).replace('.', ',')
                    FS = str(F).replace('.', ',')
                    CS = str(C).replace('.', ',')

                    cursor.execute(
                        "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {
                            'LAB_NO': LAB_NO})
                    for row in cursor.fetchall():
                        PROBEGR_IDS = (row.OBJID)
                    cursor.execute(
                        "SELECT (OBJID),(PROBAGR_OBJID) FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                            'PROBAGR_OBJID': PROBEGR_IDS})
                    for row in cursor.fetchall():
                        PROBEGR_SVODKA = (row.OBJID)
                    cursor.execute(
                        "SELECT (OBJID),(Ip),(IL),(Sr) FROM SVODKA_FIZMEX WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                            'PROBEGR_SVODKA': PROBEGR_SVODKA})
                    for row in cursor.fetchall():
                        Ip = (row.Ip)
                        IL = (row.IL)
                        Sr = (row.Sr)
                    if Sr <= 0.8:
                        CMUSL_OBJID = '96C5DAE5713940E8AFA9A4042B0851A2'
                        CMUSL_OBJID = str(CMUSL_OBJID)
                    if Sr > 0.8:
                        CMUSL_OBJID = '073E8206C7C94C0ABD2C3142F5E77EAA'
                        CMUSL_OBJID = str(CMUSL_OBJID)
                    crsr = conn.cursor()
                    crsr.execute(
                        "INSERT INTO SDOPR (OBJID,	DATA_ISP,	CMSTRGR_OBJID,	CMUSL_OBJID,	SDSPEED_OBJID,	PROBAGR_OBJID,ForFizMex,SD_Fi,SD_C,	PRIBOR_OBJID,	CONDITIONS) "
                        "VALUES ('%(OBJID)s',	'%(DATA_ISP)s',	'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0',	'%(CMUSL_OBJID)s',	'FEBBE9906CA64E269659F045A0AB6CD9',	'%(PROBEGR_IDS)s','-1','%(SD_Fi)s','%(SD_C)s',	'3D7FE26F62424351B1C994264C48E42C',	'1')"
                        % {'OBJID': SDDATA_OBJID, 'DATA_ISP': directory_time, 'PROBEGR_IDS': PROBEGR_IDS,
                           'CMUSL_OBJID': CMUSL_OBJID, 'SD_Fi': FS, 'SD_C': CS})

                    # 1 давление
                    GLUB1SD = str(Press1).replace('.', ',')
                    GLUB2SD = str(Press2).replace('.', ',')
                    GLUB3SD = str(Press3).replace('.', ',')

                    crsr.execute(
                        "INSERT INTO SDDATA (OBJID,	P,F,T,	S) "
                        "VALUES ('%(OBJID)s',	'%(P)s','%(F)s','205,52',	'40,15152')"
                        % {'OBJID': SDDATA_OBJID, 'P': GLUB1SD, 'F': st1s})

                    # 2 давление
                    crsr.execute(
                        "INSERT INTO SDDATA (OBJID,	P,F,T,	S) "
                        "VALUES ('%(OBJID)s',	'%(P)s','%(F)s','193,38',	'40,15152')"
                        % {'OBJID': SDDATA_OBJID, 'P': GLUB2SD, 'F': st2s})

                    # 3 давление
                    crsr.execute(
                        "INSERT INTO SDDATA (OBJID,	P,F,T,	S) "
                        "VALUES ('%(OBJID)s',	'%(P)s','%(F)s','212,36',	'40,15152')"
                        % {'OBJID': SDDATA_OBJID, 'P': GLUB3SD, 'F': st3s})

                    crsr.commit()

                    data_excel = xw.sheets('EngGeo')

                    df1 = (data_excel.range('B2:H16').options(pd.DataFrame, header=1, index_col=0).value)

                    df2 = (data_excel.range('O2:U16').options(pd.DataFrame, header=1, index_col=0).value)

                    df3 = (data_excel.range('H21:N35').options(pd.DataFrame, header=1, index_col=0).value)
                    for u in range(0, 14):
                        crsr.execute(
                            "INSERT INTO SDZAMER (OBJID,P,ZAMER_NUM,T,TANGENT_PRESS,SHEAR_DEF) "
                            "VALUES ('%(OBJID)s',	'%(P)s',	'%(ZAMER_NUM)s',	'%(T)s',	'%(TANGENT_PRESS)s','%(SHEAR_DEF)s')"
                            % {'OBJID': (str(df1.iloc[int(u), 0])), 'P': ((str(df1.iloc[int(u), 1])).replace('.', ',')),
                               'ZAMER_NUM': (str(df1.iloc[int(u), 2])).replace('.', ','),
                               'T': (str(df1.iloc[int(u), 3])).replace('.', ','),
                               'TANGENT_PRESS': (str(df1.iloc[int(u), 4])).replace('.', ','),
                               'SHEAR_DEF': (str(df1.iloc[int(u), 5])).replace('.', ',')})

                        crsr.execute(
                            "INSERT INTO SDZAMER (OBJID,P,ZAMER_NUM,T,TANGENT_PRESS,SHEAR_DEF) "
                            "VALUES ('%(OBJID)s',	'%(P)s',	'%(ZAMER_NUM)s',	'%(T)s',	'%(TANGENT_PRESS)s','%(SHEAR_DEF)s')"
                            % {'OBJID': (str(df2.iloc[int(u), 0])), 'P': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                               'ZAMER_NUM': (str(df2.iloc[int(u), 2])).replace('.', ','),
                               'T': (str(df2.iloc[int(u), 3])).replace('.', ','),
                               'TANGENT_PRESS': (str(df2.iloc[int(u), 4])).replace('.', ','),
                               'SHEAR_DEF': (str(df2.iloc[int(u), 5])).replace('.', ',')})

                        crsr.execute(
                            "INSERT INTO SDZAMER (OBJID,P,ZAMER_NUM,T,TANGENT_PRESS,SHEAR_DEF) "
                            "VALUES ('%(OBJID)s',	'%(P)s',	'%(ZAMER_NUM)s',	'%(T)s',	'%(TANGENT_PRESS)s','%(SHEAR_DEF)s')"
                            % {'OBJID': (str(df3.iloc[int(u), 0])), 'P': ((str(df3.iloc[int(u), 1])).replace('.', ',')),
                               'ZAMER_NUM': (str(df3.iloc[int(u), 2])).replace('.', ','),
                               'T': (str(df3.iloc[int(u), 3])).replace('.', ','),
                               'TANGENT_PRESS': (str(df3.iloc[int(u), 4])).replace('.', ','),
                               'SHEAR_DEF': (str(df3.iloc[int(u), 5])).replace('.', ',')})

                        u += 1

                    crsr.commit()
                    return write_EngGeo_SPS

                write_EngGeo_SPS()

            app.kill()

        # Компрессия
        if SPD == '+':  # SPD
            PressC = str(E)
            cursor.execute(
                "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
            for row in cursor.fetchall():
                PROBEGR_IDS = (row.OBJID)
            cursor.execute(
                "SELECT (OBJID),(PROBAGR_OBJID) FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                    'PROBAGR_OBJID': PROBEGR_IDS})
            for row in cursor.fetchall():
                PROBEGR_SVODKA = (row.OBJID)
            cursor.execute(
                "SELECT (OBJID),(Ip),(IL),(Sr),(Kpor) FROM SVODKA_FIZMEX WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                    'PROBEGR_SVODKA': PROBEGR_SVODKA})
            for row in cursor.fetchall():
                Ip = (row.Ip)
                IL = (row.IL)
                Sr = (row.Sr)
                Kpor = (row.Kpor)
            if Sr <= 0.8:
                CMUSL_OBJID = '96C5DAE5713940E8AFA9A4042B0851A2'
                CMUSL_OBJID = str(CMUSL_OBJID)
            if Sr > 0.8:
                CMUSL_OBJID = '073E8206C7C94C0ABD2C3142F5E77EAA'
                CMUSL_OBJID = str(CMUSL_OBJID)
            if Ip <= 7 and Ip > 0:
                GruntSPD = 'Супеси'
            if Ip <= 17 and Ip > 7:
                GruntSPD = 'Суглинки'
            if Ip > 17:
                GruntSPD = 'Глины'

            df_E = [E]
            df_E= pd.DataFrame(df_E)

            df_IL = [IL]
            df_IL = pd.DataFrame(df_IL)

            df_Kpor = [Kpor]
            df_Kpor = pd.DataFrame(df_Kpor)

            df_GruntSPD = [GruntSPD]
            df_GruntSPD = pd.DataFrame(df_GruntSPD)

            df_PROBEGR_IDS = [PROBEGR_IDS]
            df_PROBEGR_IDS = pd.DataFrame(df_PROBEGR_IDS)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/SPD.xlsx', mode='a', engine="openpyxl",
                                    if_sheet_exists='overlay')

            df_E.to_excel(writer, sheet_name='SPD', startcol=13, startrow=20, index=False,
                              index_label=False,
                              header=False)

            df_IL.to_excel(writer, sheet_name='SPD', startcol=13, startrow=19, index=False, index_label=False,
                               header=False)

            df_Kpor.to_excel(writer, sheet_name='SPD', startcol=9, startrow=18, index=False,
                          index_label=False,
                          header=False)

            df_GruntSPD.to_excel(writer, sheet_name='SPD', startcol=13, startrow=21, index=False,
                              index_label=False,
                              header=False)
            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_PROBEGR_IDS.to_excel(writer, sheet_name='EngGeo', startcol=1, startrow=0, index=False,
                                          index_label=False,
                                          header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/SPD.xlsx')

            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispSPD():
                    data_excel = xw.sheets('SPDVEN')
                    dfD = data_excel.range('B3:M9').options(pd.DataFrame, header=1, index_col=0).value
                    dfD.to_csv('Z:/Zapis/ISP/Stan/Test.C.log', sep='\t')  # создание лога из выведенного датафрейма
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path)
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('SPD')
                    os.chdir(File_Path + LAB_NO + '/SPD/')
                    os.mkdir(PressC)
                    os.chdir(PressC)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/SPD/' + PressC)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '20	87')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.C.log', File_Path + LAB_NO + '/SPD/' + PressC + '/Test')
                    return create_base_ispSPD

                create_base_ispSPD()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_SPD():
                    crsr.execute(
                        "INSERT INTO CMOPR (OBJID,	PROBAGR_OBJID,	DATA_ISP,	SCEMA,	H_RING1,	CMUSL_OBJID,	CMSTRGR_OBJID,	PRIBOR_OBJID, 	RAZGRUZKA,	Mk_Manual,	Nu_Manual,	PRIBORNAME_OBJID,	DATA_BEGIN_ISP,	DATA_END_ISP,	ZOOM_PERCENT,	BETA,	BETA_MANUAL,	NO_SUBSIDENCE,	W_MANUAL,	KAZAGRANDE) "
                        "VALUES ('%(OBJID)s',	'%(PROBAGR_OBJID)s',	'%(DATA_ISP)s',	'1',	'20',	'%(CMUSL_OBJID)s', 'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0',	'F81B7BFBAD47423FBBBD8D9D5AD49A71','0', '0','0','F81B7BFBAD47423FBBBD8D9D5AD49A71','%(DATA_BEGIN_ISP)s','%(DATA_END_ISP)s','100','0,6','0','0','0','0')"
                        % {'OBJID': PROBEGR_IDS, 'PROBAGR_OBJID': PROBEGR_IDS, 'DATA_ISP': directory_time,
                           'CMUSL_OBJID': CMUSL_OBJID, 'DATA_BEGIN_ISP': directory_time,
                           'DATA_END_ISP': directory_time})
                    crsr.commit()

                    data_excel = xw.sheets('EngGeo')
                    df2 = (data_excel.range('A1:Q7').options(pd.DataFrame, header=1, index_col=0).value)
                    for u in range(0, 6):
                        crsr.execute(
                            "INSERT INTO CMDATA (OBJID,	P,	isZ,	Deform1,		Deform,	st,				OtnDef,		k_tare,	k_tarez,	NRN,	ST_PRS) "
                            "VALUES ('%(OBJID)s',	'%(P)s',	'0',	'%(Deform1)s',	'%(Deform)s','%(st)s',	'%(OtnDef)s','0','0','%(NRN)s','0')"
                            % {'OBJID': (str(df2.iloc[int(u), 0])),
                               'P': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                               'Deform1': ((str(df2.iloc[int(u), 3])).replace('.', ',')),
                               'Deform': ((str(df2.iloc[int(u), 5])).replace('.', ',')),
                               'st': ((str(df2.iloc[int(u), 6])).replace('.', ',')),
                               'OtnDef': ((str(df2.iloc[int(u), 10])).replace('.', ',')),
                               'NRN': ((str(df2.iloc[int(u), 14])).replace('.', ','))})
                        u += 1

                    crsr.commit()
                    return write_EngGeo_SPD

                write_EngGeo_SPD()

            app.kill()

        # Компрессия   разгрузкой
        if SPDL == '+':  # SPDL
            PressCL = str(E)
            cursor.execute(
                "SELECT (OBJID),(LAB_NO),(GLUB_OT) FROM PROBAGR WHERE (LAB_NO) = '%(LAB_NO)s'" % {'LAB_NO': LAB_NO})
            for row in cursor.fetchall():
                PROBEGR_IDS = (row.OBJID)
            cursor.execute(
                "SELECT (OBJID),(PROBAGR_OBJID) FROM SVODKA_TBL WHERE (PROBAGR_OBJID) = '%(PROBAGR_OBJID)s'" % {
                    'PROBAGR_OBJID': PROBEGR_IDS})
            for row in cursor.fetchall():
                PROBEGR_SVODKA = (row.OBJID)
            cursor.execute(
                "SELECT (OBJID),(Ip),(IL),(Sr),(Kpor) FROM SVODKA_FIZMEX WHERE (OBJID) = '%(PROBEGR_SVODKA)s'" % {
                    'PROBEGR_SVODKA': PROBEGR_SVODKA})
            for row in cursor.fetchall():
                Ip = (row.Ip)
                IL = (row.IL)
                Il = (row.IL)
                Sr = (row.Sr)
                Kpor = (row.Kpor)
            if Sr <= 0.8:
                CMUSL_OBJID = '96C5DAE5713940E8AFA9A4042B0851A2'
                CMUSL_OBJID = str(CMUSL_OBJID)
            if Sr > 0.8:
                CMUSL_OBJID = '073E8206C7C94C0ABD2C3142F5E77EAA'
                CMUSL_OBJID = str(CMUSL_OBJID)
            if Ip <= 7 and Ip > 0:
                GruntSPD = 'Супеси'
            if Ip <= 17 and Ip > 7:
                GruntSPD = 'Суглинки'
            if Ip > 17:
                GruntSPD = 'Глины'

            df_E = [E]
            df_E = pd.DataFrame(df_E)

            df_IL = [IL]
            df_IL = pd.DataFrame(df_IL)

            df_Kpor = [Kpor]
            df_Kpor = pd.DataFrame(df_Kpor)

            df_GruntSPD = [GruntSPD]
            df_GruntSPD = pd.DataFrame(df_GruntSPD)

            df_PROBEGR_IDS = [PROBEGR_IDS]
            df_PROBEGR_IDS = pd.DataFrame(df_PROBEGR_IDS)

            writer = pd.ExcelWriter('Z:/Zapis/ISP/Grapics/SPDL.xlsx', mode='a', engine="openpyxl",
                                    if_sheet_exists='overlay')
            if Il > 0.5:
                df_E.to_excel(writer, sheet_name='SPDL m-pl', startcol=5, startrow=13, index=False,
                              index_label=False,
                              header=False)
                df_IL.to_excel(writer, sheet_name='SPDL m-pl', startcol=6, startrow=3, index=False, index_label=False,
                               header=False)
                df_Kpor.to_excel(writer, sheet_name='SPDL m-pl', startcol=6, startrow=2, index=False,
                                 index_label=False,
                                 header=False)
                df_GruntSPD.to_excel(writer, sheet_name='SPDL m-pl', startcol=6, startrow=1, index=False,
                                     index_label=False,
                                     header=False)
            if Il > 0.25 and IL <= 0.5:
                df_E.to_excel(writer, sheet_name='SPDL t-pl', startcol=5, startrow=13, index=False,
                              index_label=False,
                              header=False)
                df_IL.to_excel(writer, sheet_name='SPDL t-pl', startcol=6, startrow=3, index=False, index_label=False,
                               header=False)
                df_Kpor.to_excel(writer, sheet_name='SPDL t-pl', startcol=6, startrow=2, index=False,
                                 index_label=False,
                                 header=False)
                df_GruntSPD.to_excel(writer, sheet_name='SPDL t-pl', startcol=6, startrow=1, index=False,
                                     index_label=False,
                                     header=False)
            if Il <= 0.25:
                df_E.to_excel(writer, sheet_name='SPDL pt-pl', startcol=5, startrow=13, index=False,
                              index_label=False,
                              header=False)
                df_IL.to_excel(writer, sheet_name='SPDL pt-pl', startcol=6, startrow=3, index=False, index_label=False,
                               header=False)
                df_Kpor.to_excel(writer, sheet_name='SPDL pt-pl', startcol=6, startrow=2, index=False,
                                 index_label=False,
                                 header=False)
                df_GruntSPD.to_excel(writer, sheet_name='SPDL pt-pl', startcol=6, startrow=1, index=False,
                                     index_label=False,
                                     header=False)

            if (write_and_createISP == 1 or not_create_ISP == 1):
                df_PROBEGR_IDS.to_excel(writer, sheet_name='EngGeo', startcol=1, startrow=0, index=False,
                                        index_label=False,
                                        header=False)
            writer.close()

            app = xw.App(visible=False)
            book = app.books.open('Z:/Zapis/ISP/Grapics/SPDL.xlsx')

            if write_and_createISP == 1 or not_write_EngGeo_not_EngGeo_parametr == 1 or not_write_EngGeo == 1:
                def create_base_ispSPDL():

                    if Il > 0.5:
                        data_excel = xw.sheets('SPDLM выгрузка')
                        dfDL = data_excel.range('B3:M17').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.CL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if Il > 0.25 and Il <= 0.5:
                        data_excel = xw.sheets('SPDLT выгрузка')
                        dfDL = data_excel.range('B3:M17').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.CL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    if Il <= 0.25:
                        data_excel = xw.sheets('SPDLP выгрузка')
                        dfDL = data_excel.range('B3:M17').options(pd.DataFrame, header=1, index_col=0).value
                        dfDL.to_csv('Z:/Zapis/ISP/Stan/Test.CL.log',
                                    sep='\t')  # создание лога из выведенного датафрейма
                    # создание папок и копирование нужных файл из их директорий
                    os.chdir(File_Path)
                    os.chdir(File_Path + LAB_NO)
                    os.mkdir('SPDL')
                    os.chdir(File_Path + LAB_NO + '/SPDL/')
                    os.mkdir(PressCL)
                    os.chdir(PressCL)
                    shutil.copy('Z:/Zapis\ISP\obr_0.2.xml', File_Path + LAB_NO + '/SPDL/' + PressCL)
                    os.mkdir('General')
                    os.chdir('General')
                    my_file = open("General.log", "w+")
                    my_file.write('SampleHeight_mm	SampleDiameter_mm	\n'
                                  '20	87')
                    my_file.close()
                    os.chdir('..')
                    os.mkdir('Test')
                    os.chdir('Test')
                    shutil.copy('Z:/Zapis/ISP/Stan/Test.CL.log', File_Path + LAB_NO + '/SPDL/' + PressCL + '/Test')
                    return create_base_ispSPDL

                create_base_ispSPDL()

            if not_create_ISP == 1 or write_and_createISP == 1:
                def write_EngGeo_SPDL():
                    crsr.execute(
                        "INSERT INTO CMOPR (OBJID,	PROBAGR_OBJID,	DATA_ISP,	SCEMA,	H_RING1,	CMUSL_OBJID,	CMSTRGR_OBJID,	PRIBOR_OBJID, 	RAZGRUZKA,	Mk_Manual,	Nu_Manual,	PRIBORNAME_OBJID,	DATA_BEGIN_ISP,	DATA_END_ISP,	ZOOM_PERCENT,	BETA_MANUAL,	NO_SUBSIDENCE,	W_MANUAL,	KAZAGRANDE) "
                        "VALUES ('%(OBJID)s',	'%(PROBAGR_OBJID)s',	'%(DATA_ISP)s',	'1',	'20',	'%(CMUSL_OBJID)s', 'ECE1E86C9C3C49DBA3EC8E3E23A3BBC0',	'F81B7BFBAD47423FBBBD8D9D5AD49A71','1', '0','0','F81B7BFBAD47423FBBBD8D9D5AD49A71','%(DATA_BEGIN_ISP)s','%(DATA_END_ISP)s','35','0','0','0','0')"
                        % {'OBJID': PROBEGR_IDS, 'PROBAGR_OBJID': PROBEGR_IDS, 'DATA_ISP': directory_time,
                           'CMUSL_OBJID': CMUSL_OBJID, 'DATA_BEGIN_ISP': directory_time,
                           'DATA_END_ISP': directory_time})
                    crsr.commit()

                    data_excel = xw.sheets('EngGeo')
                    if Il > 0.5:
                        df2 = (data_excel.range('A1:Q15').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 14):
                            crsr.execute(
                                "INSERT INTO CMDATA (OBJID,	P,	isZ,	Deform1,		Deform,	st,				OtnDef,		k_tare,	k_tarez,	NRN,	ST_PRS) "
                                "VALUES ('%(OBJID)s',	'%(P)s',	'0',	'%(Deform1)s',	'%(Deform)s','%(st)s',	'%(OtnDef)s','0','0','%(NRN)s','0')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'P': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'Deform1': ((str(df2.iloc[int(u), 3])).replace('.', ',')),
                                   'Deform': ((str(df2.iloc[int(u), 5])).replace('.', ',')),
                                   'st': ((str(df2.iloc[int(u), 6])).replace('.', ',')),
                                   'OtnDef': ((str(df2.iloc[int(u), 10])).replace('.', ',')),
                                   'NRN': ((str(df2.iloc[int(u), 14])).replace('.', ','))})
                            u += 1
                        crsr.commit()
                    if Il > 0.25 and Il <= 0.5:
                        df2 = (data_excel.range('R1:AH15').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 14):
                            crsr.execute(
                                "INSERT INTO CMDATA (OBJID,	P,	isZ,	Deform1,		Deform,	st,				OtnDef,		k_tare,	k_tarez,	NRN,	ST_PRS) "
                                "VALUES ('%(OBJID)s',	'%(P)s',	'0',	'%(Deform1)s',	'%(Deform)s','%(st)s',	'%(OtnDef)s','0','0','%(NRN)s','0')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'P': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'Deform1': ((str(df2.iloc[int(u), 3])).replace('.', ',')),
                                   'Deform': ((str(df2.iloc[int(u), 5])).replace('.', ',')),
                                   'st': ((str(df2.iloc[int(u), 6])).replace('.', ',')),
                                   'OtnDef': ((str(df2.iloc[int(u), 10])).replace('.', ',')),
                                   'NRN': ((str(df2.iloc[int(u), 14])).replace('.', ','))})
                            u += 1
                        crsr.commit()
                    if Il <= 0.25:
                        df2 = (data_excel.range('AI1:AY15').options(pd.DataFrame, header=1, index_col=0).value)
                        for u in range(0, 14):
                            crsr.execute(
                                "INSERT INTO CMDATA (OBJID,	P,	isZ,	Deform1,		Deform,	st,				OtnDef,		k_tare,	k_tarez,	NRN,	ST_PRS) "
                                "VALUES ('%(OBJID)s',	'%(P)s',	'0',	'%(Deform1)s',	'%(Deform)s','%(st)s',	'%(OtnDef)s','0','0','%(NRN)s','0')"
                                % {'OBJID': (str(df2.iloc[int(u), 0])),
                                   'P': ((str(df2.iloc[int(u), 1])).replace('.', ',')),
                                   'Deform1': ((str(df2.iloc[int(u), 3])).replace('.', ',')),
                                   'Deform': ((str(df2.iloc[int(u), 5])).replace('.', ',')),
                                   'st': ((str(df2.iloc[int(u), 6])).replace('.', ',')),
                                   'OtnDef': ((str(df2.iloc[int(u), 10])).replace('.', ',')),
                                   'NRN': ((str(df2.iloc[int(u), 14])).replace('.', ','))})
                            u += 1
                    crsr.commit()
                    return write_EngGeo_SPDL

                write_EngGeo_SPDL()

            app.kill()

        r = int(
            r)  # перевод действующего R для сложения к нему +1 и продвижения по ячейкам вниз, после перевод R в строковое значение, чтобы он мог быть сложен с столбцом
        r += 1
        r = str(r)
        crsr.commit()
        print(LAB_NO)
        wbxl = xw.Book('Z:/Zapis/ISP/Shablon.xlsx')
    else:
        print(datetime.now() - start_time)
        Di = input()
except Exception as err:
    print('Исправляй  '+LAB_NO)

    logging.exception(err)