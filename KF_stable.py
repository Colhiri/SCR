import logging
import time
from datetime import datetime
from random import randint

import pandas as pd
import pyodbc

import connect_class_b as cc

my_file = open("Z:\Zapis\Object\Table_name.txt")
name_table = my_file.read()
my_file.close()
print(name_table)

NewConnect = cc.ConnectTable()
NewConnect.connect_to_googlesheet(name_table)
worksheet_journal = NewConnect.connect_to_spreadsheet('KF')
worksheet_parametr = NewConnect.connect_to_spreadsheet('Parametr')


class PrepareData:
    # перевод журнала gs в df
    pd.options.display.width = None
    pd.options.mode.chained_assignment = None

    def __init__(self, data_input):
        self.DF = None
        self.gc_object = data_input.get_values(major_dimension="COLUMNS")
        self.gc_object1 = data_input.get_values('A:B', major_dimension="rows")

    # makeFrame - создаю дф из журнала
    def makeFrame(self):
        data = {
            'LAB_NO': [d for d in self.gc_object[0]],
            'KF_soft': [d for d in self.gc_object[2]],
            'KF_hard': [d for d in self.gc_object[3]],
            'RoMin': [d for d in self.gc_object[5]],
            'RoMax': [d for d in self.gc_object[6]],
            'FIs': [d for d in self.gc_object[8]],
            'FIw': [d for d in self.gc_object[9]]
        }
        self.DF = pd.DataFrame(data).replace({'': None})
        # self.DF = self.DF.astype(dtype='float64', errors='ignore')

        return self.DF

    def makeParametr(self):
        data = {
            'path': self.gc_object1[0],
            'DELETE_FILTR': self.gc_object1[1],
            'write_KF': self.gc_object1[2],
            'write_U': self.gc_object1[3],
            'write_Ro': self.gc_object1[4]
        }
        self.DF = pd.DataFrame(data).replace({'': None})

        return self.DF


kf_data = PrepareData(worksheet_journal).makeFrame()
parametr_d = PrepareData(worksheet_parametr).makeParametr()

T = 20
K864 = 864
S = 25
gradient1, gradient2, gradient3, gradient4, gradient5 = 0.2, 0.4, 0.6, 0.8, 1

start_time = datetime.now()  # замер времени
picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))

connect_EGE = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + parametr_d.iat[0, 0] + '')
cursor_EGE = connect_EGE.cursor()

print(kf_data)

r = 1
try:
    while kf_data.iat[r, 0] != None:
        # блок вывода значений из экселя
        LAB_NO = str(kf_data.iat[r, 0]).replace(' ', '')
        LAB_NO = LAB_NO.replace('.0', '')

        KF_soft = kf_data.iat[r, 1]
        try:
            KF_soft = float(KF_soft.replace(',', '.'))
        except:
            pass

        KF_hard = kf_data.iat[r, 2]
        try:
            KF_hard = float(KF_hard.replace(',', '.'))
        except:
            pass

        RoMin = kf_data.iat[r, 3]
        try:
            RoMin = float(RoMin.replace(',', '.'))
        except:
            pass

        RoMax = kf_data.iat[r, 4]
        try:
            RoMax = float(RoMax.replace(',', '.'))
        except:
            pass

        FIs = kf_data.iat[r, 5]
        try:
            FIs = float(FIs.replace(',', '.'))
        except:
            pass

        FIw = kf_data.iat[r, 6]
        try:
            FIw = float(FIw.replace(',', '.'))
        except:
            pass

        # блок поиска лабораторки
        search_probagr = "SELECT OBJID FROM PROBAGR WHERE LAB_NO = ?"
        result_search_probagr = cursor_EGE.execute(search_probagr, LAB_NO)
        for row in cursor_EGE.fetchall():
            OBJID_PROBAGR = row.OBJID

        # Удалить ли сводку?
        if parametr_d.iat[0, 1] == '1':
            cursor_EGE.execute(
                "DELETE FROM PROBAGR_FILTR WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})
            cursor_EGE.execute(
                "DELETE FROM PROBAGR_ROMIN WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})
            cursor_EGE.execute(
                "DELETE FROM PROBAGR_ROMAX WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})
        else:
            pass

        search_probag_svodka = "SELECT OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
        result_search_probagr_svodka = cursor_EGE.execute(search_probag_svodka, OBJID_PROBAGR)
        for row in cursor_EGE.fetchall():
            PROBEGR_SVODKA = row.OBJID
        search_probag_svodka_grans = "SELECT GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,G01_005 FROM SVODKA_GRANS WHERE OBJID = ?"
        result_search_probagr_svodka_grans = cursor_EGE.execute(search_probag_svodka_grans, PROBEGR_SVODKA)
        for row in cursor_EGE.fetchall():
            GGR10 = row.GGR10
            if row.GGR10 is None:
                GGR10 = 0
            else:
                GGR10 = float(row.GGR10)
            if row.G10_5 is None:
                G10_5 = 0
            else:
                G10_5 = float(row.G10_5)
            if row.G5_2 is None:
                G5_2 = 0
            else:
                G5_2 = float(row.G5_2)
            if row.G2_1 is None:
                G2_1 = 0
            else:
                G2_1 = float(row.G2_1)
            if row.G1_05 is None:
                G1_05 = 0
            else:
                G1_05 = float(row.G1_05)
            if row.G05_025 is None:
                G05_025 = 0
            else:
                G05_025 = float(row.G05_025)
            if row.G025_01 is None:
                G025_01 = 0
            else:
                G025_01 = float(row.G025_01)
            if row.G01_005 is None:
                G01_005 = 0
            else:
                G01_005 = float(row.G01_005)

        part = G01_005


        class type_soil:
            # класс тип грунта и присвоение ему параметров расчета
            def __init__(self, kf_soft_max, kf_soft_min, sec_soft_max, sec_soft_min, kf_hard_max, kf_hard_min,
                         sec_hard_max,
                         sec_hard_min, extra_sec_plus1, extra_sec_plus2, extra_sec_plus3,
                         extra_sec_plus4, extra_sec_plus5, romin, romin_extra, romax, romax_extra, FIs, FIw, extra_FIs,
                         extra_FIw):
                self.kf_soft_max = kf_soft_max
                self.kf_soft_min = kf_soft_min
                self.sec_soft_max = sec_soft_max
                self.sec_soft_min = sec_soft_min
                self.kf_hard_max = kf_hard_max
                self.kf_hard_min = kf_hard_min
                self.sec_hard_max = sec_hard_max
                self.sec_hard_min = sec_hard_min
                self.extra_sec_plus1 = extra_sec_plus1
                self.extra_sec_plus2 = extra_sec_plus2
                self.extra_sec_plus3 = extra_sec_plus3
                self.extra_sec_plus4 = extra_sec_plus4
                self.extra_sec_plus5 = extra_sec_plus5
                self.romin = romin
                self.romin_extra = romin_extra
                self.romax = romax
                self.romax_extra = romax_extra
                self.FIs = FIs
                self.FIw = FIw
                self.extra_FIs = extra_FIs
                self.extra_FIw = extra_FIw

            # если нет значения в экселе (там где none)
            def kf_soft_none(self):
                global KF_soft, sec_soft, sec_soft1, sec_soft2, sec_soft3, sec_soft4, sec_soft5
                KF_soft = round(
                    ((((self.kf_soft_max - self.kf_soft_min) / 500) * abs(50 - part) * 10) + self.kf_soft_min), 4)
                sec_soft = (((self.sec_soft_max - self.sec_soft_min) / 500) * abs(
                    0 - part) * 10) + self.sec_soft_min
                sec_soft1 = sec_soft + - self.extra_sec_plus1
                sec_soft2 = sec_soft + - self.extra_sec_plus2
                sec_soft3 = sec_soft + - self.extra_sec_plus3
                sec_soft4 = sec_soft + - self.extra_sec_plus4
                sec_soft5 = sec_soft + - self.extra_sec_plus5

            # если есть значение в экселе (там где нет none)
            def kf_soft(self):
                global KF_soft, sec_soft, sec_soft1, sec_soft2, sec_soft3, sec_soft4, sec_soft5
                self.KF_soft = round(KF_soft, 4)
                sec_soft = (((self.sec_soft_max - self.sec_soft_min) / 500) * abs(
                    0 - part) * 10) + self.sec_soft_min
                sec_soft1 = sec_soft
                sec_soft2 = sec_soft
                sec_soft3 = sec_soft
                sec_soft4 = sec_soft
                sec_soft5 = sec_soft

            def kf_hard_none(self):
                global KF_hard, sec_hard, sec_hard1, sec_hard2, sec_hard3, sec_hard4, sec_hard5
                KF_hard = round(
                    ((((self.kf_hard_max - self.kf_hard_min) / 500) * abs(50 - part) * 10) + self.kf_hard_min), 4)
                self.KF_hard = KF_hard
                sec_hard = (((self.sec_hard_max - self.sec_hard_min) / 500) * abs(
                    0 - part) * 10) + self.sec_hard_min
                sec_hard1 = sec_hard + - self.extra_sec_plus1
                sec_hard2 = sec_hard + - self.extra_sec_plus2
                sec_hard3 = sec_hard + - self.extra_sec_plus3
                sec_hard4 = sec_hard + - self.extra_sec_plus4
                sec_hard5 = sec_hard + - self.extra_sec_plus5

            def kf_hard(self):
                global KF_hard, sec_hard, sec_hard1, sec_hard2, sec_hard3, sec_hard4, sec_hard5
                self.KF_hard = round(KF_hard, 4)
                sec_hard = (((self.sec_hard_max - self.sec_hard_min) / 500) * abs(
                    0 - part) * 10) + self.sec_hard_min
                sec_hard1 = sec_hard
                sec_hard2 = sec_hard
                sec_hard3 = sec_hard
                sec_hard4 = sec_hard
                sec_hard5 = sec_hard

            def ro_min_none(self):
                global VES1
                RoMin = (self.romin + self.romin_extra / 100)
                VES1 = (str((250 * RoMin) + 339).replace('.', ','))

            def ro_max_none(self):
                global VES1_max
                RoMax = (self.romax + self.romax_extra / 100)
                VES1_max = (str((250 * RoMax) + 339).replace('.', ','))

            def ro_max(self):
                global VES1_max
                VES1_max = (str((250 * RoMax) + 339).replace('.', ','))

            def ro_min(self):
                global VES1
                VES1 = (str((250 * RoMin) + 339).replace('.', ','))

            def fls_none(self):
                global FIs
                self.FIs = self.FIs + self.extra_FIs
                FIs = (str(self.FIs).replace('.', ','))

            def fls(self):
                global FIs
                self.FIs = (str(FIs).replace('.', ','))
                FIs = self.FIs

            def flw_none(self):
                global FIw
                self.FIw = self.FIw + self.extra_FIw
                FIw = (str(self.FIw).replace('.', ','))

            def flw(self):
                global FIw
                self.FIw = (str(FIw).replace('.', ','))
                FIw = self.FIw


        # присвоение расчетных значений для класса type_soil
        large = type_soil(40, 25, 40, 5, 12, 5, 90, 15, 0, 0, 0, 0, 0, 1.58, randint(0, 7), 1.82,
                          randint(0, 5), 32, 25, randint(0, 2), randint(0, 3))
        mid = type_soil(25, 12, 600, 54, 4.5, 2, 1200, 120, randint(0, 7), randint(0, 7), randint(0, 7), randint(0, 7),
                        randint(0, 7), 1.5, randint(0, 8), 1.75, randint(0, 7), 34, 26, randint(0, 2), randint(0, 2))
        small = type_soil(11, 4, 2400, 240, 2.5, 1, 4800, 540, randint(0, 15), randint(0, 15), randint(0, 15),
                          randint(0, 15), randint(0, 15), 1.4, randint(0, 12), 1.67, randint(0, 8), 36, 28,
                          randint(0, 2),
                          randint(0, 3))
        dust = type_soil(5, 0.9, 7200, 555, 1.2, 0.1, 14400, 1100, randint(0, 25), randint(0, 25), randint(0, 25),
                         randint(0, 25), randint(0, 25), 1.28, randint(0, 12), 1.57, randint(0, 10), 39, 21,
                         randint(0, 2),
                         randint(0, 2))


        def control_type():
            # функция для того, чтобы выяснять какой тип песка и присваивать ему нужный тип песка
            if (G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
                type_soil = large
            elif (G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
                type_soil = mid
            elif ((G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75):
                type_soil = small
            elif ((G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) < 75):
                type_soil = dust

            if KF_soft == None:
                type_soil.kf_soft_none()
            else:
                type_soil.kf_soft()
            if KF_hard == None:
                type_soil.kf_hard_none()
            else:
                type_soil.kf_hard()
            if RoMin == None:
                type_soil.ro_min_none()
            else:
                type_soil.ro_min()
            if RoMax == None:
                type_soil.ro_max_none()
            else:
                type_soil.ro_max()
            if FIs == None:
                type_soil.fls_none()
            else:
                type_soil.fls()
            if FIw == None:
                type_soil.flw_none()
            else:
                type_soil.flw()


        control_type()

        # расчет объема для каждой ступени в рыхлом и плотном состоянии
        volume_soft = ((gradient1 * KF_soft * S * sec_soft) * (3 * T + 70)) / 86400
        kf_calc_soft = 864 * ((((volume_soft) / (sec_soft * S)) / gradient1) / (0.7 + 0.03 * T))

        volume_hard = ((gradient1 * KF_hard * S * sec_hard) * (3 * T + 70)) / 86400
        kf_calc_hard = 864 * ((((volume_hard) / (sec_hard * S)) / gradient1) / (0.7 + 0.03 * T))

        volume_soft2, volume_soft3, volume_soft4, volume_soft5 = volume_soft * 2, volume_soft * 3, volume_soft * 4, \
                                                                 volume_soft * 5
        volume_hard2, volume_hard3, volume_hard4, volume_hard5 = volume_hard * 2, volume_hard * 3, volume_hard * 4, \
                                                                 volume_hard * 5
        ZAMER_NUM_soft = 0
        ZAMER_NUM_hard = 1
        METHOD = 0

        if parametr_d.iat[0, 2] == '1':
            # запись параметров (сухой и рыхлый)
            write_1_soft = ('INSERT INTO PROBAGR_FILTR (OBJID,ZAMER_NO,TIME_FILT,'
                            + 'TEMP_V,GRAD,SURF,VOL1,METHOD) VALUES (?,?,?,?,?,?,?,?)')
            sec_soft = [sec_soft1, sec_soft2, sec_soft3, sec_soft4, sec_soft5]
            gradient = [gradient1, gradient2, gradient3, gradient4, gradient5]
            vol_soft = [volume_soft, volume_soft2, volume_soft3, volume_soft4, volume_soft5]
            try:
                for sec, gradient, vol in zip(sec_soft, gradient, vol_soft):
                    write_2_soft = cursor_EGE.execute(write_1_soft, OBJID_PROBAGR, ZAMER_NUM_soft,
                                                      sec, T, gradient, S,
                                                      vol, METHOD)
            except pyodbc.IntegrityError:
                input('защита от дублирования! удалите испытания по пробе.')
                pass

            write_1_hard = ('INSERT INTO PROBAGR_FILTR (OBJID,ZAMER_NO,TIME_FILT,'
                            + 'TEMP_V,GRAD,SURF,VOL1,METHOD) VALUES (?,?,?,?,?,?,?,?)')
            sec_hard = [sec_hard1, sec_hard2, sec_hard3, sec_hard4, sec_hard5]
            gradient = [gradient1, gradient2, gradient3, gradient4, gradient5]
            vol_hard = [volume_hard, volume_hard2, volume_hard3, volume_hard4, volume_hard5]
            try:
                for sec, gradient, vol in zip(sec_hard, gradient, vol_hard):
                    write_2_hard = cursor_EGE.execute(write_1_hard, OBJID_PROBAGR, ZAMER_NUM_hard,
                                                      sec, T, gradient, S,
                                                      vol, METHOD)
            except pyodbc.IntegrityError:
                input('защита от дублирования! удалите испытания по пробе.')
                pass
        else:
            pass

        if parametr_d.iat[0, 4] == '1':
            # RoMin
            write_1_soft_min = ('INSERT INTO PROBAGR_ROMIN (OBJID,ZAMER_NO,DATA_ISP,'
                                + 'VOL0,VES0,VES1) VALUES (?,?,?,?,?,?)')

            write_2_soft_min = cursor_EGE.execute(write_1_soft_min, OBJID_PROBAGR, 0,
                                                  directory_time, 250, 339, VES1)
            # RoMax
            write_1_soft_max = ('INSERT INTO PROBAGR_ROMAX (OBJID,ZAMER_NO,DATA_ISP,'
                                + 'VOL0,VES0,VES1) VALUES (?,?,?,?,?,?)')

            write_2_soft_max = cursor_EGE.execute(write_1_soft_max, OBJID_PROBAGR, 0,
                                                  directory_time, 250, 339, VES1_max)
        else:
            pass

        if parametr_d.iat[0, 3] == '1':
            # обновление значений угла (сухой, под водой)
            cursor_EGE.execute("UPDATE SVODKA_FIZMEX SET FIs='%(FIs)s'  WHERE OBJID = '%(PROBEGR_SVODKA)s'"
                               % {'FIs': FIs, 'PROBEGR_SVODKA': PROBEGR_SVODKA})
            cursor_EGE.execute("UPDATE SVODKA_FIZMEX SET FIw='%(FIw)s'  WHERE OBJID = '%(PROBEGR_SVODKA)s'"
                               % {'FIw': FIw, 'PROBEGR_SVODKA': PROBEGR_SVODKA})
        else:
            pass

        r = int(r)
        r += 1
        connect_EGE.commit()
        print(LAB_NO)
        if r == kf_data.count()[0]:
            connect_EGE.commit()
            print(datetime.now() - start_time)
            Di = input()
            break

    connect_EGE.commit()
    print(datetime.now() - start_time)
    Di = input()
except Exception as err:
    print('Исправляй  ' + LAB_NO)
    logging.exception(err)
    Di = input()
