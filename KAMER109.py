# import MECH_right

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



my_file = open("Z:\Zapis\ISP\Table_name.txt")
name_table = my_file.read()
my_file.close()
print(name_table)

class PrepareData:
    pd.options.display.width = None
    pd.options.mode.chained_assignment = None

    def __init__(self, data_input):
        self.DF = None
        self.gc_object = data_input.get_values('A:BE', major_dimension="columns")
        self.gc_object1 = data_input.get_values('A:B', major_dimension="rows")
        self.gc_object2 = data_input.get_values('A:I', major_dimension="columns")

    # makeFrame - создаю дф из журнала
    def makeFrame(self):

        data = {'LAB_NO': [d for d in self.gc_object[0]],
                'SKV': [d for d in self.gc_object[1]],
                'GLUB': [d for d in self.gc_object[2]],
                'N_IG': [d for d in self.gc_object[3]],
                'А10': [d for d in self.gc_object[4]],
                'А5': [d for d in self.gc_object[5]],
                'А2': [d for d in self.gc_object[6]],
                'А1': [d for d in self.gc_object[7]],
                'А0,5': [d for d in self.gc_object[8]],
                'А0,25': [d for d in self.gc_object[9]],
                'А0,1': [d for d in self.gc_object[10]],
                'А0,05': [d for d in self.gc_object[11]],

                'rs': [d for d in self.gc_object[18]],
                'W': [d for d in self.gc_object[19]],
                'r': [d for d in self.gc_object[21]],
                'r,min': [d for d in self.gc_object[22]],
                'r,max': [d for d in self.gc_object[23]],
                'e': [d for d in self.gc_object[24]],
                'WL': [d for d in self.gc_object[27]],
                'Wp': [d for d in self.gc_object[28]],

                'Sr': [d for d in self.gc_object[31]],

                'Cпк': [d for d in self.gc_object[32]],
                'jпк': [d for d in self.gc_object[33]],
                'Emoed': [d for d in self.gc_object[36]],
                'Kф,max': [d for d in self.gc_object[40]],
                'Kф,min': [d for d in self.gc_object[41]],
                'Iom': [d for d in self.gc_object[42]],
                'E': [d for d in self.gc_object[43]],
                'j': [d for d in self.gc_object[44]],
                'C': [d for d in self.gc_object[45]],

                'DOP': [d for d in self.gc_object[47]],
                'DOP_plus': [d for d in self.gc_object[48]],
                'Norm': [d for d in self.gc_object[50]],
                'TPDL': [d for d in self.gc_object[52]],

                'Ip': [d for d in self.gc_object[29]],
                'IL': [d for d in self.gc_object[30]],

                'js': [d for d in self.gc_object[37]],
                'jw': [d for d in self.gc_object[38]],

                'Erzg': [d for d in self.gc_object[54]],
                'E2': [d for d in self.gc_object[55]],
                'Point_rzg': [d for d in self.gc_object[56]]
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
                if x == 'C_dispersion':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
            except:
                pass

            try:
                if x == 'F_dispersion':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
            except:
                pass

            try:
                if x == 'E_dispersion':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
            except:
                pass

            try:
                if x == 'Ro_dispersion':
                    update = float(update.replace(',', '.'))
                    data.update({x: update})
            except:
                pass


            try:
                if x == 'diap_activate':
                    update = int(update)
                    data.update({x: update})
            except:
                pass

        return data


    def makeParametrDiap(self):

        data = {'N_IG': [d for d in self.gc_object2[0]],
                'C_min': [d for d in self.gc_object2[1]],
                'C_max': [d for d in self.gc_object2[2]],
                'F_min': [d for d in self.gc_object2[3]],
                'F_max': [d for d in self.gc_object2[4]],
                'E_min': [d for d in self.gc_object2[5]],
                'E_max': [d for d in self.gc_object2[6]],
                'Ro_min': [d for d in self.gc_object2[7]],
                'Ro_max': [d for d in self.gc_object2[8]]
                }

        self.DF = pd.DataFrame(data).replace({'': None})


        diapason_FM = {}


        limiter = 2
        count_rows = len(self.DF) - 2
        for x in range(count_rows):

            N_IG = self.DF.iloc[limiter][0]

            try:
                C_min = float((self.DF.iloc[limiter][1]).replace(',', '.'))
            except:
                C_min = None


            try:
                C_max = float((self.DF.iloc[limiter][2]).replace(',', '.'))
            except:
                C_max = None

            try:
                F_min = float((self.DF.iloc[limiter][3]).replace(',', '.'))
            except:
                F_min = None

            try:
                F_max = float((self.DF.iloc[limiter][4]).replace(',', '.'))
            except:
                F_max = None

            try:
                E_min  = float((self.DF.iloc[limiter][5]).replace(',', '.'))
            except:
                E_min = None

            try:
                E_max  = float((self.DF.iloc[limiter][6]).replace(',', '.'))
            except:
                E_max = None

            try:
                Ro_min  = float((self.DF.iloc[limiter][7]).replace(',', '.'))
            except:
                Ro_min = None

            try:
                Ro_max = float((self.DF.iloc[limiter][8]).replace(',', '.'))
            except:
                Ro_max = None

            diapason_FM.setdefault(N_IG, {'C_ig': [C_min, C_max], 'F_ig': [F_min, F_max], 'E_ig': [E_min, E_max], 'Ro_ig': [Ro_min, Ro_max]})
            limiter += 1

        return diapason_FM




NewConnect = cc.ConnectTable()
NewConnect.connect_to_googlesheet(name_table)
worksheet_journal = NewConnect.connect_to_spreadsheet('FM')
worksheet_parametr = NewConnect.connect_to_spreadsheet('Parametr_FM')
diapason_FM = NewConnect.connect_to_spreadsheet('DIAP_FOR_FM')

parametr_object = PrepareData(worksheet_parametr).makeParametr()

isp_data = PrepareData(worksheet_journal).makeFrame()

# isp_data = isp_data.sort_values(by='LAB_NO')

# isp_data.to_csv(f"Z:/{'ffgg'}.log", sep='\t', index=False, header=False)


diapason_FM = PrepareData(diapason_FM).makeParametrDiap()

# name_parametr = ['LAB_NO'0, 'SKV'1, 'GLUB'2, 'N_IG'3, 'А10'4, 'А5'5, 'А2'6, 'А1'7, 'А0,5'8, 'А0,25'9, 'А0,1'10, !!!!!!!! 'rs'11, 'W'12, 'r'13,
#                  'r,min'14, 'r,max'15, 'e'16, 'WL'17, 'Wp'18, 'Sr'19, 'Cпк'20, 'jпк'21, 'Emoed'22, 'Kф,max'23, 'Kф,min'24, 'Iom'25, 'E'26,
#                  'j'27, 'C'28,,,,,,,,,,,,,'Ip'34, 'IL' 35, 'js' 36, 'jw' 37] + 1


count_rows_df = len(isp_data) - 1
for update_lab in range(1, count_rows_df + 1):
    lab_now = isp_data.iloc[update_lab][0].split('-')[0]
    if lab_now == parametr_object.get('cipher_object'):
        pass
    else:
        isp_data.iloc[update_lab][0] = f"{parametr_object.get('cipher_object')}-{parametr_object.get('year')}-{update_lab}"

    # обновление параметров глубина, от RoS до Iom (содержание органики)

    parametr_proba = [2, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 36, 37, 27, 28, 29, 21, 22, 23, 34, 35, 36, 37]
    for x in parametr_proba:
        try:
            isp_data.iloc[update_lab][x] = float((isp_data.iloc[update_lab][x].replace(',', '.')))
        except:
            pass

    # обновление грансостава на основе того, что он есть смотря по ситу А0,01
    if isp_data.iloc[update_lab][8] != None:
        fraction = [4, 5, 6, 7, 8, 9, 10, 11]
        for x in fraction:
            try:
                isp_data.iloc[update_lab][x] = float((isp_data.iloc[update_lab][x].replace(',', '.')))
            except:
                if isp_data.iloc[update_lab][x] == None:
                    isp_data.iloc[update_lab][x] = 0.0



    # обновление механики по диапазонам в зависимости от того где стоит плюс
    if parametr_object.get('diap_activate') == 1:
        N_IG = str(isp_data.iloc[update_lab][3])
        if N_IG == None:
            # расчет коэффициента пористости, а также Sr
            # if isp_data.iloc[update_lab][17] == None:
            try:
                pd_lab = isp_data.iloc[update_lab][14] / (1 + 0.01 * isp_data.iloc[update_lab][13])
                koef_por = (isp_data.iloc[update_lab][12] - pd_lab) / (pd_lab)
                isp_data.iloc[update_lab][17] = koef_por
                Sr = ((isp_data.iloc[update_lab][13] * isp_data.iloc[update_lab][12]) / (koef_por * 1)) / 100
                isp_data.iloc[update_lab][20] = Sr
            except:
                pass
            # расчет Ip , а также Il
            # if isp_data.iloc[update_lab][34] == None:
            try:
                Ip = isp_data.iloc[update_lab][18] - isp_data.iloc[update_lab][19]
                isp_data.iloc[update_lab][34] = Ip
                IL = (isp_data.iloc[update_lab][13] - isp_data.iloc[update_lab][19]) / Ip
                isp_data.iloc[update_lab][35] = IL
            except:
                pass
            continue

        parametr_Ro_activate = 0

        # cцепление
        try:
            C_diap_min = diapason_FM.get(N_IG).get('C_ig')[0]
            C_diap_max = diapason_FM.get(N_IG).get('C_ig')[1]
        except:
            C_diap_min = 1
            C_diap_max = 2



        if C_diap_min != None and C_diap_max != None:
            choise_C = randint(C_diap_min * 1000, C_diap_max * 1000) / 1000

        if C_diap_min == None:
            C_dispersion = parametr_object.get('С_dispersion')
            if C_dispersion == None:
                print('Не задан разброс по С, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_C = randint(((C_diap_max - C_dispersion / 2) * 1000),
                                    ((C_diap_max + C_dispersion / 2) * 1000)) / 1000

        if C_diap_max == None:
            C_dispersion = parametr_object.get('С_dispersion')
            if C_dispersion == None:
                print('Не задан разброс по C, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_C = randint(((C_diap_min - C_dispersion / 2) * 1000),
                                    ((C_diap_min + C_dispersion / 2) * 1000)) / 1000

        if C_diap_min == None and C_diap_max == None:
            print('Не проставлены диапазоны плотности, проставьте С min или С max и задайте диапазон разброса!')
            d = input()

        # одноплоскостной срез
        if isp_data.iloc[update_lab][21] == '#ERROR!' or isp_data.iloc[update_lab][21] == '+' or isp_data.iloc[update_lab][21] == '1' or isp_data.iloc[update_lab][21] == 1:
            isp_data.iloc[update_lab][21] = choise_C


        # трехосник
        if isp_data.iloc[update_lab][29] == '#ERROR!' or isp_data.iloc[update_lab][29] == '+' or \
                isp_data.iloc[update_lab][29] == '1'  or isp_data.iloc[update_lab][29] == 1:
            isp_data.iloc[update_lab][29] = choise_C


        # угол
        try:
            F_diap_min = diapason_FM.get(N_IG).get('F_ig')[0]
            F_diap_max = diapason_FM.get(N_IG).get('F_ig')[1]
        except:
            F_diap_min = 1
            F_diap_max = 2

        if F_diap_min == None and F_diap_max == None:
            print('Не проставлены диапазоны плотности, проставьте F min или F max и задайте диапазон разброса!')
            d = input()

        if F_diap_min != None and F_diap_max != None:
            choise_F = randint(F_diap_min * 100, F_diap_max * 100) / 100

        if F_diap_min == None:
            F_dispersion = parametr_object.get('F_dispersion')
            if F_dispersion == None:
                print('Не задан разброс по F, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_F = randint(((F_diap_max - F_dispersion / 2) * 100),
                                    ((F_diap_max + F_dispersion / 2) * 100)) / 100

        if F_diap_max == None:
            F_dispersion = parametr_object.get('F_dispersion')
            if F_dispersion == None:
                print('Не задан разброс по F, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_F = randint(((F_diap_min - F_dispersion / 2) * 100),
                                    ((F_diap_min + F_dispersion / 2) * 100)) / 100

        # name_parametr = ['LAB_NO'0, 'SKV'1, 'GLUB'2, 'N_IG'3, 'А10'4, 'А5'5, 'А2'6, 'А1'7, 'А0,5'8, 'А0,25'9, 'А0,1'10, !!!!!!!! 'rs'11, 'W'12, 'r'13,
        #                  'r,min'14, 'r,max'15, 'e'16, 'WL'17, 'Wp'18, 'Sr'19, 'Cпк'20, 'jпк'21, 'Emoed'22, 'Kф,max'23, 'Kф,min'24, 'Iom'25, 'E'26,
        #                  'j'27, 'C'28,,,,,,,,,,,,,'Ip'34, 'IL' 35, 'js' 36, 'jw' 37] + 1
        # одноплоскостной срез
        if isp_data.iloc[update_lab][22] == '#ERROR!' or isp_data.iloc[update_lab][22] == '+' or isp_data.iloc[update_lab][22] == '1' or isp_data.iloc[update_lab][22] == 1:
            isp_data.iloc[update_lab][22] = choise_F

            if isp_data.iloc[update_lab][35] == None:
                parametr_Ro_activate = 1

        # трехосник
        if isp_data.iloc[update_lab][28] == '#ERROR!' or isp_data.iloc[update_lab][28] == '+' or \
                isp_data.iloc[update_lab][28] == '1'  or isp_data.iloc[update_lab][28] == 1:
            isp_data.iloc[update_lab][28] = choise_F

            if isp_data.iloc[update_lab][35] == None:
                parametr_Ro_activate = 1

        # модуль
        try:
            E_diap_min = diapason_FM.get(N_IG).get('E_ig')[0]
            E_diap_max = diapason_FM.get(N_IG).get('E_ig')[1]
        except:
            E_diap_min = 1
            E_diap_max = 2

        if E_diap_min == None and E_diap_max == None:
            print('Не проставлены диапазоны плотности, проставьте E min или E max и задайте диапазон разброса!')
            d = input()

        if E_diap_min != None and E_diap_max != None:
            choise_E = randint(E_diap_min * 100, E_diap_max * 100) / 100

        if E_diap_min == None:
            E_dispersion = parametr_object.get('E_dispersion')
            if E_dispersion == None:
                print('Не задан разброс по E, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_E = randint(((E_diap_max - E_dispersion / 2) * 100),
                                   ((E_diap_max + E_dispersion / 2) * 100)) / 100

        if E_diap_max == None:
            E_dispersion = parametr_object.get('E_dispersion')
            if E_dispersion == None:
                print('Не задан разброс по E, добавьте его в Parametr_FM!')
                d = input()
            else:
                choise_E = randint(((E_diap_min - E_dispersion / 2) * 100),
                                   ((E_diap_min + E_dispersion / 2) * 100)) / 100

        # комрпессия
        if isp_data.iloc[update_lab][23] == '#ERROR!' or isp_data.iloc[update_lab][23] == '+' or \
                isp_data.iloc[update_lab][23] == '1':
            isp_data.iloc[update_lab][23] = choise_E

        # трехосник
        if isp_data.iloc[update_lab][27] == '#ERROR!' or isp_data.iloc[update_lab][27] == '+' or \
                isp_data.iloc[update_lab][27] == '1':
            isp_data.iloc[update_lab][27] = choise_E

        if isp_data.iloc[update_lab][27] != None or isp_data.iloc[update_lab][28] != None or isp_data.iloc[update_lab][
            18] != None or isp_data.iloc[update_lab][19] != None:
            if isp_data.iloc[update_lab][35] == None:
                parametr_Ro_activate = 1

        if parametr_Ro_activate == 1 and isp_data.iloc[update_lab][14] == None:
            # плотность
            Ro_diap_min = diapason_FM.get(N_IG).get('Ro_ig')[0]
            Ro_diap_max = diapason_FM.get(N_IG).get('Ro_ig')[1]

            if Ro_diap_min == None and Ro_diap_max == None:
                print('Не проставлены диапазоны плотности, проставьте Ro min или Ro max и задайте диапазон разброса!')
                d = input()

            if Ro_diap_min != None and Ro_diap_max != None:
                choise_Ro = randint(Ro_diap_min * 100, Ro_diap_max * 100) / 100

            if Ro_diap_min == None:
                Ro_dispersion = parametr_object.get('Ro_dispersion')
                if Ro_dispersion == None:
                    print('Не задан разброс по Ro, добавьте его в Parametr_FM!')
                    d = input()
                else:
                    choise_Ro = randint(int((Ro_diap_max - Ro_dispersion) * 100),
                                        int((Ro_diap_max + Ro_dispersion) * 100)) / 100

            if Ro_diap_max == None:
                Ro_dispersion = parametr_object.get('Ro_dispersion')
                if Ro_dispersion == None:
                    print('Не задан разброс по Ro, добавьте его в Parametr_FM!')
                    d = input()
                else:
                    choise_Ro = randint(int((Ro_diap_min - Ro_dispersion) * 100),
                                        int((Ro_diap_min + Ro_dispersion) * 100)) / 100

            isp_data.iloc[update_lab][14] = choise_Ro

        # расчет коэффициента пористости, а также Sr
        # if isp_data.iloc[update_lab][17] == None:
        try:
            pd_lab = isp_data.iloc[update_lab][14] / (1 + 0.01 * isp_data.iloc[update_lab][13])
            koef_por = (isp_data.iloc[update_lab][12] - pd_lab) / (pd_lab)
            isp_data.iloc[update_lab][17] = koef_por
            Sr = ((isp_data.iloc[update_lab][13] * isp_data.iloc[update_lab][12]) / (koef_por * 1)) / 100
            isp_data.iloc[update_lab][20] = Sr
        except:
            pass
        # расчет Ip , а также Il
        # if isp_data.iloc[update_lab][34] == None:
        try:
            Ip = isp_data.iloc[update_lab][18] - isp_data.iloc[update_lab][19]
            isp_data.iloc[update_lab][34] = Ip
            IL = (isp_data.iloc[update_lab][13] - isp_data.iloc[update_lab][19]) / Ip
            isp_data.iloc[update_lab][35] = IL
        except:
            pass

    else:

        N_IG = str(isp_data.iloc[update_lab][3])
        if N_IG == None or N_IG == 'None':
            # расчет коэффициента пористости, а также Sr
            # if isp_data.iloc[update_lab][17] == None:
            try:
                pd_lab = isp_data.iloc[update_lab][14] / (1 + 0.01 * isp_data.iloc[update_lab][13])
                koef_por = (isp_data.iloc[update_lab][12] - pd_lab) / (pd_lab)
                isp_data.iloc[update_lab][17] = koef_por
                Sr = ((isp_data.iloc[update_lab][13] * isp_data.iloc[update_lab][12]) / (koef_por * 1)) / 100
                isp_data.iloc[update_lab][20] = Sr
            except:
                pass
            # расчет Ip , а также Il
            # if isp_data.iloc[update_lab][34] == None:
            try:
                Ip = isp_data.iloc[update_lab][18] - isp_data.iloc[update_lab][19]
                isp_data.iloc[update_lab][34] = Ip
                IL = (isp_data.iloc[update_lab][13] - isp_data.iloc[update_lab][19]) / Ip
                isp_data.iloc[update_lab][35] = IL
            except:
                pass

        else:
            # расчет коэффициента пористости, а также Sr
            # if isp_data.iloc[update_lab][17] == None:
            try:
                pd_lab = isp_data.iloc[update_lab][14] / (1 + 0.01 * isp_data.iloc[update_lab][13])
                koef_por = (isp_data.iloc[update_lab][12] - pd_lab) / (pd_lab)
                isp_data.iloc[update_lab][17] = koef_por
                Sr = ((isp_data.iloc[update_lab][13] * isp_data.iloc[update_lab][12]) / (koef_por * 1)) / 100
                isp_data.iloc[update_lab][20] = Sr
            except:
                pass
            # расчет Ip , а также Il
            # if isp_data.iloc[update_lab][34] == None:
            try:
                Ip = isp_data.iloc[update_lab][18] - isp_data.iloc[update_lab][19]
                isp_data.iloc[update_lab][34] = Ip
                IL = (isp_data.iloc[update_lab][13] - isp_data.iloc[update_lab][19]) / Ip
                isp_data.iloc[update_lab][35] = IL
            except:
                pass


        parametr_Ro_activate = 0

        if isp_data.iloc[update_lab][27] != None or isp_data.iloc[update_lab][28] != None or isp_data.iloc[update_lab][18] != None or isp_data.iloc[update_lab][19] != None:
            parametr_Ro_activate = 1

        if parametr_Ro_activate == 1 and isp_data.iloc[update_lab][14] == None and N_IG != 'None':
            # плотность
            try:
                Ro_diap_min = diapason_FM.get(N_IG).get('Ro_ig')[0]
            except:
                pass
            Ro_diap_max = diapason_FM.get(N_IG).get('Ro_ig')[1]

            if Ro_diap_min == None and Ro_diap_max == None:
                print('Не проставлены диапазоны'
                      ' плотности, проставьте Ro min или Ro max и задайте диапазон разброса!')
                d = input()

            if Ro_diap_min != None and Ro_diap_max != None:
                choise_Ro = randint(Ro_diap_min * 100, Ro_diap_max * 100) / 100

            if Ro_diap_min == None:
                Ro_dispersion = parametr_object.get('Ro_dispersion')
                if Ro_dispersion == None:
                    print('Не задан разброс по Ro, добавьте его в Parametr_FM!')
                    d = input()
                else:
                    choise_Ro = randint(int((Ro_diap_max - Ro_dispersion) * 100),
                                        int((Ro_diap_max + Ro_dispersion) * 100)) / 100

            if Ro_diap_max == None:
                Ro_dispersion = parametr_object.get('Ro_dispersion')
                if Ro_dispersion == None:
                    print('Не задан разброс по Ro, добавьте его в Parametr_FM!')
                    d = input()
                else:
                    choise_Ro = randint(int((Ro_diap_min - Ro_dispersion) * 100),
                                        int((Ro_diap_min + Ro_dispersion) * 100)) / 100

            isp_data.iloc[update_lab][14] = choise_Ro

        # расчет коэффициента пористости, а также Sr
        # if isp_data.iloc[update_lab][17] == None:
        try:
            pd_lab = isp_data.iloc[update_lab][14] / (1 + 0.01 * isp_data.iloc[update_lab][13])
            koef_por = (isp_data.iloc[update_lab][12]-pd_lab)/(pd_lab)
            isp_data.iloc[update_lab][17] = koef_por
            Sr = ((isp_data.iloc[update_lab][13] * isp_data.iloc[update_lab][12]) / (koef_por * 1)) / 100
            isp_data.iloc[update_lab][20] = Sr
        except:
            pass
        # расчет Ip , а также Il
        # if isp_data.iloc[update_lab][34] == None:
        try:
            Ip = isp_data.iloc[update_lab][18] - isp_data.iloc[update_lab][19]
            isp_data.iloc[update_lab][34] = Ip
            IL = (isp_data.iloc[update_lab][13]-isp_data.iloc[update_lab][19]) / Ip
            isp_data.iloc[update_lab][35] = IL
        except:
            pass

# name_parametr = ['LAB_NO'0, 'SKV'1, 'GLUB'2, 'N_IG'3, 'А10'4, 'А5'5, 'А2'6, 'А1'7, 'А0,5'8, 'А0,25'9, 'А0,1'10, !!!!!!!! 'rs'11, 'W'12, 'r'13,
#                  'r,min'14, 'r,max'15, 'e'16, 'WL'17, 'Wp'18, 'Sr'19, 'Cпк'20, 'jпк'21, 'Emoed'22, 'Kф,max'23, 'Kф,min'24, 'Iom'25, 'E'26,
#                  'j'27, 'C'28, 'DOP' 29, 'DOP_plus' 30, 'Norm' 31, 'TPDL' 32,,,,,,,,,'Ip'34, 'IL' 35, 'js' 36, 'jw' 37, 'Erzg' 38, 'E2' 39, 'Point_rzg' 40] + 1



def make_parametr_isp(isp_data, limiter):
    parametr_isp = {}

    if isp_data.iloc[limiter][28] != None:
        TPS = 1
        C = isp_data.iloc[limiter][29]
        F = isp_data.iloc[limiter][28]
        if parametr_object.get('random_F') is not None and int(parametr_object.get('random_F')) == 1:
            F += randint(1, 5) / 100

        if parametr_object.get('glub_DOP') != None and float(str(parametr_object.get('glub_DOP')).replace(',','.')) <= isp_data.iloc[limiter][2]:
            DOP = 1
            DOPplus = float(str(parametr_object.get('how_DOP')).replace(',','.'))
        else:
            DOP = None
            DOPplus = None

    else:
        TPS = None


    if isp_data.iloc[limiter][27] != None and isp_data.iloc[limiter][33] == None and ((parametr_object.get('glub_TPDL') != None and float(str(parametr_object.get('glub_TPDL')).replace(',', '.')) >= isp_data.iloc[limiter][2]) or parametr_object.get('glub_TPDL') == None):
        TPD = 1
        E = isp_data.iloc[limiter][27]
        if parametr_object.get('random_E') is not None and int(parametr_object.get('random_E')) == 1:
            E += randint(1, 5) / 100
    else:
        TPD = None


    if isp_data.iloc[limiter][21] != None:
        SPS = 1
        C = isp_data.iloc[limiter][21]
        F = isp_data.iloc[limiter][22]
        if parametr_object.get('random_F') is not None and int(parametr_object.get('random_F')) == 1:
            F += randint(1, 5) / 100

        if parametr_object.get('glub_DOP') != None and float(str(parametr_object.get('glub_DOP')).replace(',', '.')) <= isp_data.iloc[limiter][2]:
            DOP = 1
            DOPplus = float(str(parametr_object.get('how_DOP')).replace(',', '.'))
        else:
            DOP = None
            DOPplus = None
    else:
        SPS = None


    if isp_data.iloc[limiter][23] != None:
        SPD = 1
        E = isp_data.iloc[limiter][23]
    else:
        SPD = None


    if (isp_data.iloc[limiter][27] != None and isp_data.iloc[limiter][33] != None) or (isp_data.iloc[limiter][27] != None and parametr_object.get('glub_TPDL') != None and float(str(parametr_object.get('glub_TPDL')).replace(',', '.')) <= isp_data.iloc[limiter][2]):
        TPDL = 1
        E = isp_data.iloc[limiter][27]
        Erzg = isp_data.iloc[limiter][38]
        E2 = isp_data.iloc[limiter][39]
        Point_rzg = isp_data.iloc[limiter][40]
        if parametr_object.get('random_E') is not None and int(parametr_object.get('random_E')) == 1:
            E += randint(1, 5) / 100
    else:
        TPDL = None
        Erzg = None
        E2 = None
        Point_rzg = None


    if isp_data.iloc[limiter][28] == None and isp_data.iloc[limiter][21] == None:
        TPS = None
        SPS = None

        C = None
        F = None

        DOP = None
        DOPplus = None


    if parametr_object.get('glub_DOP') == None or (parametr_object.get('glub_DOP') != None and float(str(parametr_object.get('glub_DOP')).replace(',', '.')) >= isp_data.iloc[limiter][2]):
        DOP = None
        DOPplus = None


    if isp_data.iloc[limiter][23] == None and isp_data.iloc[limiter][27] == None and isp_data.iloc[limiter][33] == None:
        TPD = None
        SPD = None
        TPDL = None


        E = None
        Erzg = None
        E2 = None
        Point_rzg = None



    LAB_NO = isp_data.iloc[limiter][0]

    Grunt = None

    if isp_data.iloc[limiter][32] != None:
        Norm = 1
    else:
        Norm = None

    GLUB_DOP = None



    value_parametr = [TPS, TPD, SPS, SPD, TPDL, '#', LAB_NO, Grunt, C, F, E, DOP,
                     GLUB_DOP, DOPplus, Norm, Erzg, E2, Point_rzg]
    name_column = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    name_parametr = ['TPS', 'TPD', 'SPS', 'SPD', 'TPDL', 'limiter', 'LAB_NO', 'Grunt', 'C', 'F', 'E', 'DOP',
                     'GLUB_DOP', 'DOPplus', 'Norm', 'Erzg', 'E2', 'Point_rzg']
    for name_column, name_parametr, value in zip(name_column, name_parametr, value_parametr):
        parametr_isp.setdefault(name_parametr, value)

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


### Запись объекта в инжгео, чтобы работать дальше
###
###
### Запись объекта в инжгео, чтобы работать дальше
### Запись объекта в инжгео, чтобы работать дальше
### Запись объекта в инжгео, чтобы работать дальше
### Запись объекта в инжгео, чтобы работать дальше


def search(cursor):

    bucs_W = {}
    bucs_WL = {}
    bucs_WP = {}
    rings = {}

    # бюксы влажности
    select = "SELECT OBJID,P,num FROM Bucs WHERE P > 20"
    OBJID_BUC = list(cursor.execute(select).fetchall())

    for x in range(len(OBJID_BUC)):
        bucs_W.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])

    # бюксы текучка
    select = "SELECT OBJID,P,num FROM Bucs WHERE P > 10 and P < 20"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs_WL.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])

    # бюксы раскат
    select = "SELECT OBJID,P,num FROM Bucs WHERE P < 10"
    OBJID_BUC = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_BUC)):
        bucs_WP.setdefault(OBJID_BUC[x][0], [OBJID_BUC[x][1], OBJID_BUC[x][2]])

    # кольца
    select = "SELECT OBJID,P,V,NUM FROM Rings WHERE P > 50"
    OBJID_RING = list(cursor.execute(select).fetchall())
    for x in range(len(OBJID_RING)):
        rings.setdefault(OBJID_RING[x][0], [OBJID_RING[x][1], OBJID_RING[x][2], OBJID_RING[x][3]])

    return bucs_W, bucs_WL, bucs_WP, rings

# name_parametr = ['LAB_NO'0, 'SKV'1, 'GLUB'2, 'N_IG'3, 'А10'4, 'А5'5, 'А2'6, 'А1'7, 'А0,5'8, 'А0,25'9, 'А0,1'10, !!!!!!!! 'rs'11, 'W'12, 'r'13,
#                  'r,min'14, 'r,max'15, 'e'16, 'WL'17, 'Wp'18, 'Sr'19, 'Cпк'20, 'jпк'21, 'Emoed'22, 'Kф,max'23, 'Kф,min'24, 'Iom'25, 'E'26,
#                  'j'27, 'C'28,,,,,,,,,,,,,'Ip'34, 'IL' 35, 'js' 36, 'jw' 37] + 1

def parametr_lab(isp_data):

    # isp_data.iloc[update_lab][35]

    lab_in_object = {}

    count_rows_df = len(isp_data) - 1
    for update_lab in range(1, count_rows_df + 1):

        SKV = isp_data.iloc[update_lab][1]
        GLUB = isp_data.iloc[update_lab][2]
        LAB_NO = isp_data.iloc[update_lab][0]

        W = isp_data.iloc[update_lab][13]
        Ro = isp_data.iloc[update_lab][14]
        Wl = isp_data.iloc[update_lab][18]
        Wp = isp_data.iloc[update_lab][19]

        Ip = isp_data.iloc[update_lab][34]
        IL = isp_data.iloc[update_lab][35]
        e = isp_data.iloc[update_lab][17]
        Sr = isp_data.iloc[update_lab][20]

        Ves = 100.0
        А10 = 0 if isp_data.iloc[update_lab][4] == None and Ip == None else isp_data.iloc[update_lab][4]
        A5 = 0 if isp_data.iloc[update_lab][5] == None and Ip == None else isp_data.iloc[update_lab][5]
        A2 = 0 if isp_data.iloc[update_lab][6] == None and Ip == None else isp_data.iloc[update_lab][6]
        A1 = 0 if isp_data.iloc[update_lab][7] == None and Ip == None else isp_data.iloc[update_lab][7]
        A05 = 0 if isp_data.iloc[update_lab][8] == None and Ip == None else isp_data.iloc[update_lab][8]
        A025 = 0 if isp_data.iloc[update_lab][9] == None and Ip == None else isp_data.iloc[update_lab][9]
        A01 = 0 if isp_data.iloc[update_lab][10] == None and Ip == None else isp_data.iloc[update_lab][10]
        A005 = 0 if isp_data.iloc[update_lab][11] == None and Ip == None else isp_data.iloc[update_lab][11]

        Ip = isp_data.iloc[update_lab][34]
        IL = isp_data.iloc[update_lab][35]
        e = isp_data.iloc[update_lab][17]
        Sr = isp_data.iloc[update_lab][20]

        r_min = isp_data.iloc[update_lab][15]
        r_max = isp_data.iloc[update_lab][16]
        kf_soft_sv = isp_data.iloc[update_lab][24]
        kf_hard_sv = isp_data.iloc[update_lab][25]
        js = isp_data.iloc[update_lab][36]
        jw = isp_data.iloc[update_lab][37]

        lab_in_object.setdefault(LAB_NO,
                                 [SKV, GLUB, LAB_NO, W, Ro, Wl, Wp, Ves, А10, A5, A2, A1, A05, A025, A01, A005, Ip,
                                  IL, e, Sr, r_min, r_max, kf_soft_sv, kf_hard_sv, js, jw])
    # lab_in_object.setdefault(LAB_NO,
    #                          [SKV 0, GLUB 1, LAB_NO 2, W 3, Ro 4, Wl 5 , Wp 6, Ves 7, А10 8, A5 9, A2 10, A1 11, A05 12, A025 13, A01 14, A005 15, Ip 16,
    #                           IL 17, e 18, Sr 19, r_min 20, r_max 21, kf_min 22, kf_max 23, js 24, jw 25])

    return lab_in_object

def new_dict(lab_in_object, bucs_W, bucs_WL, bucs_WP, rings):
    new_dict = {}

    new_dict_for_ENGGEO = {}
    for LAB_NO in lab_in_object.keys():
        print(LAB_NO)
        list_parametr = lab_in_object.get(LAB_NO)

        try:
            Ip = list_parametr[16]
        except:
            Ip = None

        skv = list_parametr[0]
        depth_ot = list_parametr[1]
        lab_num = list_parametr[2]

        # роспись влажности
        W_value = list_parametr[3]
        K_W = (randint(10, 50)) / 100
        if Ip == None:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W1 = float(str(W_value).replace(',', '.'))
            m1 = float((randint(5000, 8000)) / 100)
            m0 = (float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)))

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w0, wet_w0, dry_w0 = NUM, m1, m0
            bucs_w1, wet_w1, dry_w1 = '', '', ''
        else:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W1 = float(str(W_value).replace(',', '.')) + K_W
            m1 = float((randint(5000, 8000)) / 100)
            m0 = (float((W1 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)))

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w0, wet_w0, dry_w0 = NUM, m1, m0

            # 2 бюкс
            BUCS_OBJID = random_BUC(bucs_W)
            W2 = float(str(W_value).replace(',', '.')) - K_W
            m1 = float((randint(5000, 8000)) / 100)
            m0 = (float((W2 * bucs_W.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100)))

            NUM = str(bucs_W.get(BUCS_OBJID)[1])

            bucs_w1, wet_w1, dry_w1 = NUM, m1, m0

        # роспись плотности
        Ro_value = list_parametr[4]
        if Ip != None and Ro_value != None:
            RING_OBJID = random_BUC(rings)
            VES_0 = float(rings.get(RING_OBJID)[0])
            OBJEM_0 = float(rings.get(RING_OBJID)[1])

            VES1R = (float(str(Ro_value).replace(',', '.')) * OBJEM_0 + VES_0)

            NUM = str(rings.get(RING_OBJID)[2])

            ring_num, soil_weight = NUM, VES1R
        else:
            ring_num, soil_weight = '', ''

        # роспись текучки
        WL_value = list_parametr[5]
        K_W = (randint(10, 50)) / 100
        if Ip != None:


            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_WL)
            W1 = float(str(WL_value).replace(',', '.')) + K_W
            m1 = float((randint(3500, 5000)) / 100)
            m0 = (float((W1 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)))

            NUM = str(bucs_WL.get(BUCS_OBJID)[1])

            bucs_wl0, wet_wl0, dry_wl0 = NUM, m1, m0

            # 2 бюкс
            BUCS_OBJID = random_BUC(bucs_WL)
            W2 = float(str(WL_value).replace(',', '.')) - K_W
            m1 = float((randint(3500, 5000)) / 100)
            m0 = (float((W2 * bucs_WL.get(BUCS_OBJID)[0] + 100 * m1) / (W2 + 100)))

            NUM = str(bucs_WL.get(BUCS_OBJID)[1])

            bucs_wl1, wet_wl1, dry_wl1 = NUM, m1, m0

        else:
            bucs_wl0, wet_wl0, dry_wl0 = '', '', ''
            bucs_wl1, wet_wl1, dry_wl1 = '', '', ''

        # роспись раската
        WP_value = list_parametr[6]
        if Ip != None:
            # 1 бюкс
            BUCS_OBJID = random_BUC(bucs_WP)
            W1 = float(str(WP_value).replace(',', '.'))
            m1 = float((randint(1500, 1800)) / 100)
            m0 = (float((W1 * bucs_WP.get(BUCS_OBJID)[0] + 100 * m1) / (W1 + 100)))

            NUM = str(bucs_WP.get(BUCS_OBJID)[1])

            bucs_wp0, wet_wp0, dry_wp0 = NUM, m1, m0

        else:
            bucs_wp0, wet_wp0, dry_wp0 = '', '', ''

        # роспись ГС

        if list_parametr[14] != None:
            try:
                vesgss = float(str(list_parametr[7]).replace(',', '.'))
            except:
                vesgss = ''
            try:
                a10 = float(str(list_parametr[8]).replace(',', '.'))
            except:
                a10 = ''
            try:
                a5 = float(str(list_parametr[9]).replace(',', '.'))
            except:
                a5 = ''
            try:
                a2 = float(str(list_parametr[10]).replace(',', '.'))
            except:
                a2 = ''
            try:
                a1 = float(str(list_parametr[11]).replace(',', '.'))
            except:
                a1 = ''
            try:
                a05 = float(str(list_parametr[12]).replace(',', '.'))
            except:
                a05 = ''
            try:
                a025 = float(str(list_parametr[13]).replace(',', '.'))
            except:
                a025 = ''
            try:
                a01 = float(str(list_parametr[14]).replace(',', '.'))
            except:
                a01 = ''

        else:
            vesgss, a10, a5, a2, a1, a05, a025, a01 = '', '', '', '', \
                '', '', '', ''

        # Grunt
        # [SKV 0 , GLUB 1, LAB_NO 2, W 3, Ro 4,  Wl 5, Wp 6, Ves 7, А10 8, A5 9, A2 10, A1  11, A05 12, A025 13, A01 14, A005 15, Ip 16,
        #                                   IL 17, e 18, Sr 19]

        Ip = list_parametr[16]
        IL = list_parametr[17]
        Sr = list_parametr[19]
        Kpor = list_parametr[18]
        Ro = list_parametr[4]
        W = list_parametr[3]

        # основной тип грунта для механики
        if Ip == None:
            consistency = None
            water_saturation = None
            IL = None
            main_type = 'incoherent'  # несвязный
#
#
            GGR10 = list_parametr[8]
            G10_5 = list_parametr[9]
            G5_2 = list_parametr[10]
            G2_1 = list_parametr[11]
            G1_05 = list_parametr[12]
            G05_025 = list_parametr[13]
            G025_01 = list_parametr[14]
            G01_005 = list_parametr[15]
#
            fraction_grans = [GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01, G01_005]
            fraction_index = [int(x) for x in range(8)]
            for grans, index in zip(fraction_grans, fraction_index):
                if grans == None:
                    fraction_grans[index] = 0
#
            GGR10 = fraction_grans[0]
            G10_5 = fraction_grans[1]
            G5_2 = fraction_grans[2]
            G2_1 = fraction_grans[3]
            G1_05 = fraction_grans[4]
            G05_025 = fraction_grans[5]
            G025_01 = fraction_grans[6]
            G01_005 = fraction_grans[7]
#
            # гравелистый
            if (G5_2 + G10_5 + GGR10) > 25:
                grunt_type = 'гравелистый'
                density = None
#
                # крупный
            elif (G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
                grunt_type = 'крупный'
                density = None
#
                # средний
            elif (G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) > 50:
                grunt_type = 'средний'
                if Kpor != None:
                    if Kpor <= 0.55:
                        density = 'plotn'  # плотность
                    if 0.55 < Kpor and Kpor <= 0.7:
                        density = 'mid_plotn'
                    if Kpor > 0.7:
                        density = 'pihl'
                else:
                    density = None
#
                #  мелкий
            elif (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) >= 75:
                grunt_type = 'мелкий'
                if Kpor != None:
                    if Kpor <= 0.6:
                        density = 'plotn'
                    if 0.6 < Kpor and Kpor <= 0.75:
                        density = 'mid_plotn'
                    if Kpor > 0.75:
                        density = 'pihl'
                else:
                    density = None
#
                #  пылеватый
            elif (G025_01 + G05_025 + G1_05 + G2_1 + G5_2 + G10_5 + GGR10) < 75:
                grunt_type = 'пылеватый'
                density = None
#
            Main_type = 'песок'  # пески
            Type_disp = grunt_type
        else:
            Ip = float(Ip)
            IL = float(IL)
            density = None
            main_type = 'coherent'  # связный
            # супесь
            if Ip <= 7:
                grunt_type = 'Супесь'
                if IL < 0:
                    consistency = 'Твердая'
                if 0 <= IL and IL <= 1:
                    consistency = 'Пластичная'
                if 1 < IL:
                    consistency = 'Текучая'
#
            # суглинок
            if 7 < Ip and Ip <= 17:
                grunt_type = 'Суглинок'
                if IL < 0:
                    consistency = 'Твердый'
                if 0 <= IL <= 0.25:
                    consistency = 'Полутвердый'
                if 0.25 < IL and IL <= 0.5:
                    consistency = 'Тугопластичный'
                if 0.5 < IL and IL <= 0.75:
                    consistency = 'Мягкопластичный'
                if 0.75 < IL and IL <= 1:
                    consistency = 'Текучепластичный'
                if 1 < IL:
                    consistency = 'Текучий'
#
            # глина
            if Ip > 17:
                grunt_type = 'Глина'
                if IL < 0:
                    consistency = 'Твердая'
                if 0 <= IL and IL <= 0.25:
                    consistency = 'Полутвердая'
                if 0.25 < IL and IL <= 0.5:
                    consistency = 'Тугопластичная'
                if 0.5 < IL and IL <= 0.75:
                    consistency = 'Мягкопластичная'
                if 0.75 < IL and IL <= 1:
                    consistency = 'Текучепластичная'
                if 1 < IL:
                    consistency = 'Текучая'
#
#
#
            if grunt_type == 'Супесь':
#
                Main_type = grunt_type  # супесь
                Type_disp = consistency
#
            if grunt_type == 'Суглинок':
                if Ip > 12:
                    Main_type = f"{grunt_type} тяжёлый"  # Суглинок
                    Type_disp = consistency
                else:
                    Main_type = f"{grunt_type} легкая"  # Глина
                    Type_disp = consistency
#
            if grunt_type == 'Глина':
                if Ip > 27:
                    Main_type = f"{grunt_type} тяжёлая"  # Глина
                    Type_disp = consistency
                else:
                    Main_type = f"{grunt_type} легкая"  # Глина
                    Type_disp = consistency


        new_dict[LAB_NO] = [skv, depth_ot, lab_num,
         bucs_w0, wet_w0, dry_w0,
         bucs_w1, wet_w1, dry_w1,
         ring_num, soil_weight,
         bucs_wl0, wet_wl0, dry_wl0,
         bucs_wl1, wet_wl1, dry_wl1,
         bucs_wp0, wet_wp0, dry_wp0,
         vesgss, a10, a5, a2, a1, a05, a025, a01, Main_type, Type_disp]

        new_dict_for_ENGGEO[LAB_NO] = ['Y', skv, depth_ot, lab_num,
                            bucs_w0, wet_w0, dry_w0,
                            bucs_w1, wet_w1, dry_w1,
                            ring_num, '', soil_weight,
                            bucs_wl0, wet_wl0, dry_wl0,
                            bucs_wl1, wet_wl1, dry_wl1,
                            bucs_wp0, wet_wp0, dry_wp0,
                            vesgss, a10, a5, a2, a1, a05, a025, a01]

    return new_dict, new_dict_for_ENGGEO, list_parametr


def random_BUC(dict_bucs):

    BUCS_OBJID = random.choice(list(dict_bucs))

    return BUCS_OBJID


# main part
# main part
# main part

try:
    start_time = datetime.now()  # замер времени

    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))


    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + parametr_object.get('path') + '')
    cursor = conn.cursor()

    object = input('Введите краткое название объекта:  ')

    # получение словаря по бюксам, кольцам
    bucs_W, bucs_WL, bucs_WP, rings = search(cursor)

    try:
        select = "SELECT OBJID FROM WOBJECT WHERE NAMEOBJ_SHORT = ?"
        OBJID_OBJECT = list(cursor.execute(select, object).fetchall()[0])[0]
        if OBJID_OBJECT is not None:
            parametr_write_obj = 0
            d = input('Объект найден в базе, запись КФ и МЕХ будет производитсья в него\n '
                      'Если вам это не нудно удалите объект вручную и повторите запись, если нужно - нажмите ENTER')
        else:
            print('Новый объект')
            OBJID_OBJECT = None
            parametr_write_obj = 0
    except:
        print('Новый объект')
        OBJID_OBJECT = None
        parametr_write_obj = 0




    # создание параметров лабораторки
    lab_in_object = parametr_lab(isp_data)
    new_dict, new_dict_for_ENGGEO, list_parametr = new_dict(lab_in_object, bucs_W, bucs_WL, bucs_WP, rings)

    if parametr_write_obj == 0:
        df = pd.DataFrame(new_dict)
        df = df.transpose()

        df = df.rename(columns={
            0: "n_skv", 1: "depth_from", 2: "lab_num",
            3: "bucs_w0", 4: "wet_w0", 5: "dry_w0",
            6: "bucs_w1", 7: "wet_w1", 8: "dry_w1",
            9: 'ring_num', 10: "ro_weight",
            11: "bucs_wl0", 12: "wet_wl0", 13: "dry_wl0",
            14: "bucs_wl1", 15: "wet_wl1", 16: "dry_wl1",
            17: "bucs_wp0", 18: "wet_wp0", 19: "dry_wp0",
            20: "gss_weight", 21: "a10", 22: "a5", 23: "a2",
            24: "a1", 25: "a05", 26: "a025", 27: "a01"
        })
        space_list = [
            [3, 'space_date', ''],
            [4, 'space_w0', ''],
            [8, 'space_w1', ''],
            [12, 'space_ro0', ''],
            [14, 'space_ro1', ''],
            [16, 'space_wl0', ''],
            [20, 'space_wl1', ''],
            [24, 'space_wp0', ''],
            [28, 'space_gss', ''],
            [37, 'space_gss_1', '']]


        for i in space_list:
            df.insert(i[0], i[1], i[2])

        har_list = ["depth_from", "wet_w0", "dry_w0", "wet_w1", "dry_w1",
                    "ro_weight", "wet_wl0", "dry_wl0", "wet_wl1", "dry_wl1",
                    "wet_wp0", "dry_wp0", "gss_weight", "a10", "a5", "a2", "a1",
                    "a05", "a025", "a01"]

        df[har_list] = df[har_list].astype("float64", errors='ignore')
        df[har_list] = df[har_list].round(2)
        df[har_list] = df[har_list].astype("str")
        df[har_list] = df[har_list].stack().str.replace('.', ',', regex=True).unstack()
        df.fillna('')
        sorted_df = df.sort_values(by='lab_num')
        sorted_df = sorted_df.transpose()


        sorted_df.to_csv(f"Z:/Zapis/ISP/First_data_object/{object}.log.log", sep='\t', index=False, header=False)






        #
        #
        #
        #
        #
        # запись объекта в EngGeo

        # генератор id
        def OBJID():
            OBJID = (''.join([random.choice(list('1234567890ABCDEF'))
                              for x in range(32)]))
            return OBJID


        def search_and_create_object(cursor, name_table, parametr_d):
            try:
                select = "SELECT OBJID FROM WOBJECT WHERE NAMEOBJ_SHORT = ?"
                OBJID_OBJECT = list(cursor.execute(select, name_table).fetchall()[0])[0]
            except:
                OBJID_OBJECT = None

            if OBJID_OBJECT != None:
                parametr_write = input('Объект найден в базе, записать его в существующий объект? (y/n):  ')
                if parametr_write == 'y':
                    return OBJID_OBJECT
                if parametr_write == 'n':
                    OBJID_OBJECT = OBJID()
                    cursor.execute(
                        f"INSERT INTO WOBJECT (OBJID, NAMEOBJ_SHORT, NAMEOBJ_FULL, DATE1, DATE2, OBJTYPE_OBJID, REGION_OBJID) VALUES ('{OBJID_OBJECT}', '{name_table}', '{name_table}', '{directory_time}', '{directory_time}', 'C40C7AF7123742F585DA2A3592CEC6EE', '5965D9FA0B2042C3B9F5CEF7EF4540F4')")
                    cursor.commit()
                    return OBJID_OBJECT

            if OBJID_OBJECT == None:
                OBJID_OBJECT = OBJID()
                cursor.execute(
                    f"INSERT INTO WOBJECT (OBJID, NAMEOBJ_SHORT, NAMEOBJ_FULL, DATE1, DATE2, OBJTYPE_OBJID, REGION_OBJID) VALUES ('{OBJID_OBJECT}', '{name_table}', '{name_table}', '{directory_time}', '{directory_time}', 'C40C7AF7123742F585DA2A3592CEC6EE', '5965D9FA0B2042C3B9F5CEF7EF4540F4')")
                cursor.commit()
                return OBJID_OBJECT


        def search_and_create_skv(cursor, OBJID_OBJECT, parametr_d, parametr_proba, name_table):
            try:
                select = "SELECT OBJID,N_SKV,AWORK_OBJID FROM SK WHERE N_SKV = ? and AWORK_OBJID = ?"
                OBJID_SKV = list(cursor.execute(select, parametr_proba.get('NO_SKV'), OBJID_OBJECT).fetchall()[0])[0]
            except:
                OBJID_SKV = None

            if OBJID_SKV != None:
                return OBJID_SKV
            else:
                OBJID_SKV = OBJID()
                cursor.execute(
                    f"INSERT INTO SK (OBJID, OBJECT, N_SKV, DIAM, VYRTYPE_OBJID, AWORK_OBJID, NSKV4SORT, DATASOURCE_ID, IS_STAT_SK) VALUES ('{OBJID_SKV}', '{name_table}', '{parametr_proba.get('NO_SKV')}', '0', '4F21D49AC7874F9795EDC4F52E559F55', '{OBJID_OBJECT}', '0000000009', '00000000000000000000000000000000', '0')")
                cursor.commit()

                # ПЕРЕЗАПИСЬ СКВАЖИНЫ (ПРИВЯЗКА)
                cursor.execute(
                    f"INSERT INTO SK_PER_OBJECT (SK_OBJID, WOBJ_OBJID) VALUES ('{OBJID_SKV}','{OBJID_OBJECT}')")
                cursor.commit()

            return OBJID_SKV


        def search_and_create_proba(cursor, OBJID_OBJECT, OBJID_SKV, parametr_d, parametr_proba, name_table):
            try:
                select = "SELECT OBJID,LAB_NO,COD FROM PROBAGR WHERE LAB_NO = ? and COD = ?"
                OBJID_LAB = list(cursor.execute(select, parametr_proba.get('LAB_NO'), OBJID_SKV).fetchall()[0])[0]
            except:
                OBJID_LAB = None

            if OBJID_LAB != None:
                OBJID_LAB = None
                return OBJID_LAB
            else:
                OBJID_LAB = OBJID()
                cursor.execute(
                    f"INSERT INTO PROBAGR (OBJID, LAB_NO, DATA_OTBORA, GLUB_OT, GLUB_DO, COD, USE_IN_STAT, CALC_UNDER_FORMULA, IS_STAT_PROBA) VALUES ('{OBJID_LAB}','{parametr_proba.get('LAB_NO')}', '{directory_time}', '{parametr_proba.get('GLUB_OT')}', '{str(float(parametr_proba.get('GLUB_OT').replace(',', '.')) + 0.2).replace('.', ',')}', '{OBJID_SKV}', '-1', '-1', '0')")
                cursor.commit()
                cursor.execute(f"INSERT INTO PROBAGR_OBJID (OBJID) VALUES ('{OBJID_LAB}')")
                cursor.commit()

                return OBJID_LAB


        def search_BUC(cursor, parametr_d, parametr_proba, type_buc):
            select = "SELECT OBJID,P,num FROM Bucs WHERE num = ?"
            try:
                OBJID_BUC = list(cursor.execute(select, type_buc).fetchall()[0])[0]
                VES_0 = list(cursor.execute(select, type_buc).fetchall()[0])[1]
            except:
                OBJID_BUC = None
                VES_0 = None
            if OBJID_BUC != None:
                return OBJID_BUC, VES_0
            else:
                print('Бюкс не найден!  ', type_buc)
                return OBJID_BUC, VES_0


        def search_RING(cursor, parametr_d, parametr_proba):
            select = "SELECT OBJID,P,V,NUM FROM Rings WHERE NUM = ?"
            try:
                RING_OBJID = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[0]
                VES0R = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[1]
                VR = list(cursor.execute(select, parametr_proba.get('RING')).fetchall()[0])[2]
            except:
                RING_OBJID = None
                VES0R = None
                VR = None
            if RING_OBJID != None:
                return RING_OBJID, VES0R, VR
            else:
                print('Кольцо не найдено!')
                return RING_OBJID, VES0R, VR


        def create_W(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            if parametr_proba.get('BUC_W_1') != None and parametr_proba.get('VES_VLGR_W_1') != None and parametr_proba.get(
                    'VES_SHGR_W_1') != None:
                OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_W_1'))
                if OBJID_BUC != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_W_1')}', '{parametr_proba.get('VES_SHGR_W_1')}')")
                    cursor.commit()
            if parametr_proba.get('BUC_W_2') != None and parametr_proba.get('VES_VLGR_W_2') != None and parametr_proba.get(
                    'VES_SHGR_W_2') != None:
                OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_W_2'))
                if OBJID_BUC != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_W (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_W_2')}', '{parametr_proba.get('VES_SHGR_W_2')}')")
                    cursor.commit()
            return True


        def create_WL(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            if parametr_proba.get('BUC_WL_1') != None and parametr_proba.get(
                    'VES_VLGR_WL_1') != None and parametr_proba.get(
                    'VES_SHGR_WL_1') != None:
                OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WL_1'))
                if OBJID_BUC != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WL_1')}', '{parametr_proba.get('VES_SHGR_WL_1')}')")
                    cursor.commit()
            if parametr_proba.get('BUC_WL_2') != None and parametr_proba.get(
                    'VES_VLGR_WL_2') != None and parametr_proba.get(
                    'VES_SHGR_WL_2') != None:
                OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WL_2'))
                if OBJID_BUC != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_WL (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WL_2')}', '{parametr_proba.get('VES_SHGR_WL_2')}')")
                    cursor.commit()
            return True


        def create_WP(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            if parametr_proba.get('BUC_WP') != None and parametr_proba.get('VES_VLGR_WP') != None and parametr_proba.get(
                    'VES_SHGR_WP') != None:
                OBJID_BUC, VES_0 = search_BUC(cursor, parametr_d, parametr_proba, parametr_proba.get('BUC_WP'))
                if OBJID_BUC != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_WP (OBJID, ZAMER_NO, DATA_ISP, BUCS_OBJID, VES0, VES_VLGR, VES_SHGR) VALUES ('{OBJID_LAB}','0', '{directory_time}', '{OBJID_BUC}', '{str(VES_0).replace('.', ',')}', '{parametr_proba.get('VES_VLGR_WP')}', '{parametr_proba.get('VES_SHGR_WP')}')")
                    cursor.commit()
            return True


        def create_RING(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            if parametr_proba.get('RING') != None and parametr_proba.get('VES_RING') != None:
                RING_OBJID, VES0R, VR = search_RING(cursor, parametr_d, parametr_proba)
                if RING_OBJID != None:
                    cursor.execute(
                        f"INSERT INTO PROBAGR_PLOTNGR (OBJID, ZAMER_NO, DATA_ISP, RING_OBJID, VES0, VES1, VOL,ROP) VALUES ('{OBJID_LAB}','1', '{directory_time}', '{RING_OBJID}', '{str(VES0R).replace('.', ',')}', '{parametr_proba.get('VES_RING')}', '{str(VR).replace('.', ',')}','0,9')")
                    cursor.commit()
            return True


        def GRANSOST(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            if parametr_proba.get('VES1') != None:
                cursor.execute(
                    f"INSERT INTO PROBAGR_GRANSOST (OBJID,DATA_ISP,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,VES1) VALUES ('{OBJID_LAB}','{directory_time}','{parametr_proba.get('GGR10')}','{parametr_proba.get('G10_5')}','{parametr_proba.get('G5_2')}','{parametr_proba.get('G2_1')}','{parametr_proba.get('G1_05')}','{parametr_proba.get('G05_025')}','{parametr_proba.get('G025_01')}', '{parametr_proba.get('VES1')}')")

                cursor.commit()

            return True


        def SVODKA_FM(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table):
            OBJID_SVODKA = OBJID()

            Ro = (lab_in_object.get(parametr_proba.get('LAB_NO'))[4])
            WL = (lab_in_object.get(parametr_proba.get('LAB_NO'))[5])

            if (WL != None and WL != 'None'):
                cursor.execute(
                    f"INSERT INTO SVODKA_TBL (OBJID, PROBAGR_OBJID) VALUES ('{OBJID_SVODKA}','{OBJID_LAB}')")
                cursor.commit()

                cursor.execute(
                    f"INSERT INTO SVODKA_FIZMEX (OBJID, OKAT_OBJID) VALUES ('{OBJID_SVODKA}','0569236D89ED49708409DA08E3DA6510')")
            if (Ro != 'None' or Ro != None) and (WL == None or WL == 'None'):

                select_prgr = "SELECT (OBJID), (PROBAGR_OBJID) FROM SVODKA_TBL_SPEC WHERE (LOCK_TYPEGR) = ?"
                result_search = cursor.execute(select_prgr, 0).fetchall()
                result_search = list(result_search[0])

                PAST_OBJ_SV = result_search[0]
                PROBAGR_OBJID_PAST = result_search[1]

                # ПЕРЕПЕШИ ЗАПРОС SELECT ЧТОБЫ ПОЛУЧАТЬ НУЖНЫЙ НОМЕР КОТОЫРЙ ПРОШЛЫЙ

                select_prgr = "UPDATE SVODKA_TBL_SPEC SET PROBAGR_OBJID = ? WHERE OBJID = ?"
                cursor.execute(select_prgr, OBJID_LAB, PAST_OBJ_SV)

                cursor.commit()

                select_prgr = "UPDATE SVODKA_TBL_SPEC SET OBJID = ? WHERE PROBAGR_OBJID = ?"
                cursor.execute(select_prgr, OBJID_SVODKA, OBJID_LAB)

                cursor.commit()

                cursor.execute(
                    f"INSERT INTO SVODKA_TBL (OBJID, PROBAGR_OBJID, LOCKS) SELECT OBJID, PROBAGR_OBJID, LOCKS FROM SVODKA_TBL_SPEC")

                cursor.commit()


                Ro = str(Ro).replace('.',',')
                try:
                    cursor.execute(
                        f"INSERT INTO SVODKA_FIZMEX (OBJID, OKAT_OBJID, Ro) VALUES ('{OBJID_SVODKA}','0569236D89ED49708409DA08E3DA6510', '{Ro}')")
                except:
                    pass
            cursor.commit()

            return OBJID_SVODKA


#lab    _in_object.setdefault(LAB_NO,
#                                    [SKV, GLUB, LAB_NO, W, Ro, Wl, Wp, Ves, А10, A5, A2, A1, A05, A025, A01, A005, Ip,
#                                      IL, e, Sr])
        # main part
        # main part
        # main part




        df = pd.DataFrame(new_dict_for_ENGGEO)
        df = df.transpose()


        df = df.rename(columns={0: "LIMITER",
            1: "NO_SKV", 2: "GLUB_OT", 3: "LAB_NO",
            4: "BUC_W_1", 5: "VES_VLGR_W_1", 6: "VES_SHGR_W_1",
            7: "BUC_W_2", 8: "VES_VLGR_W_2", 9: "VES_SHGR_W_2",
            10: 'RING', 11: "RING_VES", 12: "VES_RING",
            13: "BUC_WL_1", 14: "VES_VLGR_WL_1", 15: "VES_SHGR_WL_1",
            16: "BUC_WL_2", 17: "VES_VLGR_WL_2", 18: "VES_SHGR_WL_2",
            19: "BUC_WP", 20: "VES_VLGR_WP", 21: "VES_SHGR_WP",
            22: "VES1", 23: "GGR10", 24: "G10_5", 25: "G5_2",
            26: "G2_1", 27: "G1_05", 28: "G05_025", 29: "G025_01"
        })

        har_list = ["GLUB_OT", "VES_VLGR_W_1", "VES_SHGR_W_1", "VES_SHGR_W_2", "VES_VLGR_W_2",
                    "VES_RING", "VES_VLGR_WL_1", "VES_SHGR_WL_1", "VES_VLGR_WL_2", "VES_SHGR_WL_2",
                    "VES_VLGR_WP", "VES_SHGR_WP", "VES1", "GGR10", "G10_5", "G5_2", "G2_1",
                    "G1_05", "G05_025", "G025_01"]


        df[har_list] = df[har_list].astype("float64", errors='ignore')
        df[har_list] = df[har_list].round(2)
        df[har_list] = df[har_list].astype("str")
        df[har_list] = df[har_list].stack().str.replace('.', ',', regex=True).unstack()
        df.fillna('')
        sorted_df = df.sort_values(by='LAB_NO')




        name_table = object

        parametr_d = parametr_object

        print(parametr_d.get('path'))

        conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + parametr_d.get('path') + '')
        cursor = conn.cursor()

        directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

        try:
            parametr_proba_df = sorted_df

            parametr_proba = {}

            name_parametr = ['NO_SKV']

            parametr_proba.setdefault('NO_SKV', parametr_proba_df.iloc[1][1])

            if parametr_proba.get('NO_SKV') == 'None':
                parametr_proba.update({'NO_SKV': None})

            if parametr_proba.get('NO_SKV') == '':
                parametr_proba.update({'NO_SKV': None})

            OBJID_OBJECT = search_and_create_object(cursor, name_table, parametr_d)




            count_rows_df = len(parametr_proba_df)
            for update_lab in range(count_rows_df):

                parametr_proba = {}

                num_row = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                           26, 27, 28, 29]
                name_parametr = ['LIMITER', 'NO_SKV', 'GLUB_OT', 'LAB_NO', 'BUC_W_1', 'VES_VLGR_W_1', 'VES_SHGR_W_1',
                                 'BUC_W_2',
                                 'VES_VLGR_W_2', 'VES_SHGR_W_2', 'RING', 'RING_VES', 'VES_RING', 'BUC_WL_1',
                                 'VES_VLGR_WL_1',
                                 'VES_SHGR_WL_1', 'BUC_WL_2', 'VES_VLGR_WL_2', 'VES_SHGR_WL_2', 'BUC_WP', 'VES_VLGR_WP',
                                 'VES_SHGR_WP', 'VES1', 'GGR10', 'G10_5', 'G5_2',
                                 'G2_1', 'G1_05', 'G05_025', 'G025_01']
                name_parametr_replace = ['GLUB_OT', 'VES_VLGR_W_1', 'VES_SHGR_W_1',
                                         'VES_VLGR_W_2', 'VES_SHGR_W_2', 'RING_VES', 'VES_RING', 'VES_VLGR_WL_1',
                                         'VES_SHGR_WL_1', 'VES_VLGR_WL_2', 'VES_SHGR_WL_2', 'VES_VLGR_WP',
                                         'VES_SHGR_WP', 'VES1', 'GGR10', 'G10_5', 'G5_2',
                                         'G2_1', 'G1_05', 'G05_025', 'G025_01']
                list_int_keys_parametr_proba = ['BUC_W_1', 'BUC_W_2',
                                                'RING', 'RING_VES', 'BUC_WL_1',
                                                'BUC_WL_2', 'BUC_WP']

                for num_row, name_parametr in zip(num_row, name_parametr):
                    parametr_proba.setdefault(name_parametr, parametr_proba_df.iloc[update_lab][num_row])

                for x in parametr_proba.keys():
                    update = parametr_proba.get(x)
                    if update == 'None':
                        parametr_proba.update({x: None})

                for x in parametr_proba.keys():
                    update = parametr_proba.get(x)
                    if update == '':
                        parametr_proba.update({x: None})

                for x in list_int_keys_parametr_proba:
                    try:
                        parametr_proba.update({x: int(parametr_proba.get(x))})
                    except:
                        pass

                for x in name_parametr_replace:
                    try:
                        parametr_proba.update({x: parametr_proba.get(x).replace('.', ',')})
                    except:
                        pass

                if parametr_proba.get('LIMITER') == 'Y':

                    OBJID_SKV = search_and_create_skv(cursor, OBJID_OBJECT, parametr_d, parametr_proba, name_table)

                    OBJID_LAB = search_and_create_proba(cursor, OBJID_OBJECT, OBJID_SKV, parametr_d, parametr_proba,
                                                        name_table)

                    OBJID_SVODKA = SVODKA_FM(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba,
                                             name_table)

                    if OBJID_LAB != None:
                        create_W(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                        create_WL(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                        create_WP(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                        create_RING(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)

                        GRANSOST(cursor, OBJID_OBJECT, OBJID_SKV, OBJID_LAB, parametr_d, parametr_proba, name_table)



                        print(parametr_proba.get('LAB_NO'))


            print('Запись объекта в EngGeo завершена')
        except Exception as err:
            print('Исправляй  ' + parametr_proba.get('LAB_NO'))
            logging.exception(err)
            Di = input()

    #
    #
    #
    #
    # запись КФ

    # lab_in_object.setdefault(LAB_NO,
    #                          [SKV 0, GLUB 1, LAB_NO 2, W 3, Ro 4, Wl 5 , Wp 6, Ves 7, А10 8, A5 9, A2 10, A1 11, A05 12, A025 13, A01 14, A005 15, Ip 16,
    #                           IL 17, e 18, Sr 19, r_min 20, r_max 21, kf_soft_sv 22, kf_hard_sv 23, js 24, jw 25])

    T = 20
    K864 = 864
    S = 25
    gradient1, gradient2, gradient3, gradient4, gradient5 = 0.2, 0.4, 0.6, 0.8, 1

    start_time = datetime.now()  # замер времени
    picture_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))

    try:
        for lab in lab_in_object.keys():

            if lab_in_object.get(lab)[22] == '+' or lab_in_object.get(lab)[22] == '#ERROR!' or lab_in_object.get(lab)[22] == '+' or lab_in_object.get(lab)[22] == '1' or lab_in_object.get(lab)[22] == 1 or lab_in_object.get(lab)[22] != None:

                # блок вывода значений из экселя
                LAB_NO = lab

                # блок поиска лабораторки
                search_probagr = "SELECT OBJID FROM PROBAGR WHERE LAB_NO = ?"
                result_search_probagr = cursor.execute(search_probagr, LAB_NO)
                for row in cursor.fetchall():
                    OBJID_PROBAGR = row.OBJID

                search_probag_svodka = "SELECT OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
                result_search_probagr_svodka = cursor.execute(search_probag_svodka, OBJID_PROBAGR)
                for row in cursor.fetchall():
                    PROBEGR_SVODKA = row.OBJID

                KF_soft = lab_in_object.get(lab)[22]

                KF_hard = lab_in_object.get(lab)[23]

                RoMin = lab_in_object.get(lab)[20]

                RoMax = lab_in_object.get(lab)[21]

                FIs = lab_in_object.get(lab)[24]

                FIw = lab_in_object.get(lab)[25]

                # lab_in_object.setdefault(LAB_NO,
                #                          [SKV 0, GLUB 1, LAB_NO 2, W 3, Ro 4, Wl 5 , Wp 6, Ves 7, А10 8, A5 9, A2 10, A1 11, A05 12, A025 13, A01 14, A005 15, Ip 16,
                #                           IL 17, e 18, Sr 19, r_min 20, r_max 21, kf_soft_sv 22, kf_hard_sv 23, js 24, jw 25])

                GGR10 = lab_in_object.get(lab)[8]

                G10_5 = lab_in_object.get(lab)[9]

                G5_2 = lab_in_object.get(lab)[10]

                G2_1 = lab_in_object.get(lab)[11]

                G1_05 = lab_in_object.get(lab)[12]

                G05_025 = lab_in_object.get(lab)[13]

                G025_01 = lab_in_object.get(lab)[14]

                G01_005 = lab_in_object.get(lab)[15]

                part = G01_005


                cursor.execute(
                    "DELETE FROM PROBAGR_FILTR WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})
                cursor.execute(
                    "DELETE FROM PROBAGR_ROMIN WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})
                cursor.execute(
                    "DELETE FROM PROBAGR_ROMAX WHERE (OBJID) = '%(PROBAGR_OBJID)s'" % {'PROBAGR_OBJID': OBJID_PROBAGR})


                class type_soil:
                    # класс тип грунта и присвоение ему параметров расчета
                    def __init__(self, kf_soft_max, kf_soft_min, sec_soft_max, sec_soft_min, kf_hard_max, kf_hard_min,
                                 sec_hard_max,
                                 sec_hard_min, extra_sec_plus1, extra_sec_plus2, extra_sec_plus3,
                                 extra_sec_plus4, extra_sec_plus5, romin, romin_extra, romax, romax_extra, FIs, FIw,
                                 extra_FIs,
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
                            ((((self.kf_soft_max - self.kf_soft_min) / 500) * abs(50 - part) * 10) + self.kf_soft_min),
                            4)
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
                            ((((self.kf_hard_max - self.kf_hard_min) / 500) * abs(50 - part) * 10) + self.kf_hard_min),
                            4)
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
                mid = type_soil(25, 12, 600, 54, 4.5, 2, 1200, 120, randint(0, 7), randint(0, 7), randint(0, 7),
                                randint(0, 7),
                                randint(0, 7), 1.5, randint(0, 8), 1.75, randint(0, 7), 34, 26, randint(0, 2),
                                randint(0, 2))
                small = type_soil(11, 4, 2400, 240, 2.5, 1, 4800, 540, randint(0, 15), randint(0, 15),
                                  randint(0, 15),
                                  randint(0, 15), randint(0, 15), 1.4, randint(0, 12), 1.67, randint(0, 8), 36,
                                  28,
                                  randint(0, 2),
                                  randint(0, 3))
                dust = type_soil(5, 0.9, 7200, 555, 1.2, 0.1, 14400, 1100, randint(0, 25), randint(0, 25),
                                 randint(0, 25),
                                 randint(0, 25), randint(0, 25), 1.28, randint(0, 12), 1.57, randint(0, 10), 39,
                                 21,
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

                    if KF_soft == None or KF_soft == '#ERROR!':
                        type_soil.kf_soft_none()
                    else:
                        type_soil.kf_soft()
                    if KF_hard == None or KF_hard == '#ERROR!':
                        type_soil.kf_hard_none()
                    else:
                        type_soil.kf_hard()
                    if RoMin == None or RoMin == '#ERROR!':
                        type_soil.ro_min_none()
                    else:
                        type_soil.ro_min()
                    if RoMax == None or RoMax == '#ERROR!':
                        type_soil.ro_max_none()
                    else:
                        type_soil.ro_max()
                    if FIs == None or FIs == '#ERROR!':
                        type_soil.fls_none()
                    else:
                        type_soil.fls()
                    if FIw == None or FIw == '#ERROR!':
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

                write_KF = parametr_object.get('write_KF')


                if write_KF == '1' or write_KF == 1:
                    # запись параметров (сухой и рыхлый)
                    write_1_soft = ('INSERT INTO PROBAGR_FILTR (OBJID,ZAMER_NO,TIME_FILT,'
                                    + 'TEMP_V,GRAD,SURF,VOL1,METHOD) VALUES (?,?,?,?,?,?,?,?)')
                    sec_soft = [sec_soft1, sec_soft2, sec_soft3, sec_soft4, sec_soft5]
                    gradient = [gradient1, gradient2, gradient3, gradient4, gradient5]
                    vol_soft = [volume_soft, volume_soft2, volume_soft3, volume_soft4, volume_soft5]
                    try:
                        for sec, gradient, vol in zip(sec_soft, gradient, vol_soft):
                            write_2_soft = cursor.execute(write_1_soft, OBJID_PROBAGR, ZAMER_NUM_soft,
                                                              sec, T, gradient, S,
                                                              vol, METHOD)

                            cursor.commit()
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
                            write_2_hard = cursor.execute(write_1_hard, OBJID_PROBAGR, ZAMER_NUM_hard,
                                                              sec, T, gradient, S,
                                                              vol, METHOD)

                            cursor.commit()
                    except pyodbc.IntegrityError:
                        input('защита от дублирования! удалите испытания по пробе.')
                        pass


                else:
                    pass


                write_Ro = parametr_object.get('write_Ro')
                write_U = parametr_object.get('write_U')

                if write_Ro == '1' or write_Ro == 1:
                    # RoMin
                    write_1_soft_min = ('INSERT INTO PROBAGR_ROMIN (OBJID,ZAMER_NO,DATA_ISP,'
                                        + 'VOL0,VES0,VES1) VALUES (?,?,?,?,?,?)')

                    write_2_soft_min = cursor.execute(write_1_soft_min, OBJID_PROBAGR, 0,
                                                          directory_time, 250, 339, VES1)
                    # RoMax
                    write_1_soft_max = ('INSERT INTO PROBAGR_ROMAX (OBJID,ZAMER_NO,DATA_ISP,'
                                        + 'VOL0,VES0,VES1) VALUES (?,?,?,?,?,?)')

                    write_2_soft_max = cursor.execute(write_1_soft_max, OBJID_PROBAGR, 0,
                                                          directory_time, 250, 339, VES1_max)

                    cursor.commit()
                else:
                    pass

                if write_U == '1' or write_U == 1:
                    # обновление значений угла (сухой, под водой)
                    cursor.execute("UPDATE SVODKA_FIZMEX SET FIs='%(FIs)s'  WHERE OBJID = '%(PROBEGR_SVODKA)s'"
                                       % {'FIs': FIs, 'PROBEGR_SVODKA': PROBEGR_SVODKA})
                    cursor.execute("UPDATE SVODKA_FIZMEX SET FIw='%(FIw)s'  WHERE OBJID = '%(PROBEGR_SVODKA)s'"
                                       % {'FIw': FIw, 'PROBEGR_SVODKA': PROBEGR_SVODKA})

                    cursor.commit()
                else:
                    pass


                cursor.commit()
                print(LAB_NO)

        cursor.commit()
        print(datetime.now() - start_time)
        print('Запись КФ завершена')
    except Exception as err:

        logging.exception(err)
        Di = input()


    # сделать запись в сводку, чтобы плотность там была и т.д. и т.п.


    # сразу добавить рисовку самой сводки для проб, потому что она дообновиться сама, туда нужно просто пихнуть самое необходимое для проги



    # потом сделать роспись КФа, также не забудь указать Содержание органических веществ, а

    # словари для механики фактически готовы, остается только правильно их назвать и заменять параметры или просто сделать правильный обмен между этими словарями
    




    # добавить в прогу дорисовку влажности если есть один бюкс, дорисовку плотности по нормативкам, расчет IL, IP и т.д.

    # запись механики
    # запись механики
    # запись механики
    # запись механики
    # запись механики
    # запись механики
    # запись механики

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
    def getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor, limiter, isp_data):
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


        Ip = isp_data.iloc[limiter][34]
        IL = isp_data.iloc[limiter][35]
        Sr = isp_data.iloc[limiter][20]
        Kpor = isp_data.iloc[limiter][17]
        Ro = isp_data.iloc[limiter][14]
        W = isp_data.iloc[limiter][13]
        RoS = isp_data.iloc[limiter][12]

        # основной тип грунта для механики
        if Ip == None:
            consistency = None
            water_saturation = None
            IL = None
            main_type = 'incoherent'  # несвязный


            GGR10 = isp_data.iloc[limiter][4]
            G10_5 = isp_data.iloc[limiter][5]
            G5_2 = isp_data.iloc[limiter][6]
            G2_1 = isp_data.iloc[limiter][7]
            G1_05 = isp_data.iloc[limiter][8]
            G05_025 = isp_data.iloc[limiter][9]
            G025_01 = isp_data.iloc[limiter][10]
            G01_005 = isp_data.iloc[limiter][11]


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

        param_proba = ['PROBEGR_IDS', 'GLUB', 'PROBEGR_SVODKA', 'grunt_type', 'consistency', 'density',
                       'water_saturation',
                       'main_type', 'Ip', 'IL', 'Sr', 'Kpor', 'Ro', 'W', 'RoS', 'CMUSL_OBJID',
                       'parametr_write_temporary']
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
    def create_CM3OPR(cursor, parametr_proba, parametr_isp):
        directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        ZOOM = randint(120, 130) if parametr_isp.get('TPS') != None and parametr_isp.get('DOP') != None else randint(70, 80)
        CM3DATA_OBJID = generator_mech_objid()
        write_1 = (
                'INSERT INTO CM3OPR (OBJID,	PROBEGR_ID,	DATE_TEST,	SCHEMA,	STOCK_AREA,	AREA,	HEIGHT,	ZOOM_PERCENT,	PRIBOR_OBJID) '
                + 'VALUES (?,?,?,?,?,?,?,?,?)')
        write_2 = cursor.execute(write_1, CM3DATA_OBJID, parametr_proba.get('PROBEGR_IDS'),
                                 directory_time, 2, -777777, 1134.115, 76,
                                 ZOOM, 'F70EC2ACDCCA4FB19C2C16C0DAD8CD38')
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
                if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get(
                        'grunt_type') == 'large_sand':
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

        if parametr_d.get('what_delete') == 1 and (
                parametr_isp.get('TPS') != None or parametr_isp.get('TPD') != None or parametr_isp.get('TPDL') != None):
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
                    CM3DATA_OBJID = create_CM3OPR(cursor, parametr_proba, parametr_isp)
            except:
                CM3DATA_OBJID = create_CM3OPR(cursor, parametr_proba, parametr_isp)

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
        st2 = parametr_press.get('press_2')*(2*math.tan(math.pi*parametr_isp.get('F')/180)*((((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))+2*((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)+(2*((2*math.tan(math.pi*parametr_isp.get('F')/180)*((((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))+2*((math.tan(math.pi*parametr_isp.get('F')/180))**2)+1)**(1/2))*parametr_isp.get('C'))

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
                fake_e1_for_press[x] = randint(1, 5) / 10000

            c = (st / (math.atan(((e1_array[index] / curve)) ** 0.5)) - (
                        press / (math.atan(((e1_array[index] / curve)) ** 0.5))))
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

            X_move = z * g * -e1_array_tail[0] ** 2 + 2 * Y_move * z * g * -e1_array_tail[0] + p_array_1[
                -1] + Y_move ** 2 * z * g - z * r ** 2

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

            c = (st / (math.atan(((e1_array[-1] / curve)) ** 0.5)) - (
                        press / (math.atan(((e1_array[-1] / curve)) ** 0.5))))

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


    def ISP_TPS(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_proba, press, parametr_d, parametr_press,
                vert_speed, random_start_e1, otn_def):

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
        action_none_value[4] = 'Start'
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
        step_press = (press * 1000 - randint(1, 10) / 10000) / (count_point_loadstage - 1)
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
        VerticalStrain_loadstage = (VerticalDeformation_mm_loadstage - first_cell_e1) / (
                    volume_76 - (definirion_e1_array))

        # otn_vol_def
        definirion_ev_array = np.asarray([float(0) for x in range(count_point_loadstage)])
        volume = np.asarray([float(86149) for x in range(count_point_loadstage)])
        first_cell_ev = np.asarray([float(0) for x in range(count_point_loadstage)])
        VolumeStrain_loadstage = (VolumeDeformation_cm3_loadstage - first_cell_ev) / (volume - (definirion_ev_array))

        # wait
        # wait
        # wait
        # wait
        time_wait = np.arange(round(time_loadstage[-1], 2),
                              round(time_loadstage[-1] + parametr_d.get('reconsolidation'), 2),
                              round(randint(290, 310) / 100, 2))
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
        CellPress_kPa_wait = np.asarray(
            [float(CellPress_kPa_loadstage[-1]) for x in range(count_point_wait)]) - random_CELL

        VerticalPress_kPa_wait = CellPress_kPa_wait

        random_VERT_wait = np.asarray([float(randint(0, 2) / 100) for x in range(count_point_wait)])
        VerticalDeformation_mm_wait = np.asarray(
            [float(VerticalDeformation_mm_loadstage[-1]) for x in range(count_point_wait)]) - random_VERT_wait

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

        time_Stabilization = np.arange(round(time_wait[-1], 2), round(time_wait[-1] + end_point_time_stab, 2),
                                       round(step, 2))

        count_point_Stabilization = len(time_Stabilization)

        action_Stabilization = [str('Wait') for x in range(count_point_Stabilization)]

        action_changed_Stabilization = [str('') for x in range(count_point_Stabilization)]
        action_changed_Stabilization[-1] = True

        Deviator_kPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

        Deviator_MPa_Stabilization = [float(0) for x in range(count_point_Stabilization)]

        list_1000 = [float(1000) for x in range(count_point_Stabilization)]

        random_CELL = np.asarray([float(randint(0, 50) / 100) for x in range(count_point_Stabilization)])
        CellPress_kPa_Stabilization = np.asarray(
            [float(CellPress_kPa_wait[-1]) for x in range(count_point_Stabilization)]) - random_CELL

        VerticalPress_kPa_Stabilization = CellPress_kPa_Stabilization

        random_VERT_wait = np.asarray([float(randint(0, 2) / 100) for x in range(count_point_Stabilization)])
        VerticalDeformation_mm_Stabilization = np.asarray([float(round(VerticalDeformation_mm_wait[-1], 2)) for x in
                                                           range(count_point_Stabilization)]) - random_VERT_wait

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
        VerticalStrain_Stabilization = (VerticalDeformation_mm_Stabilization - first_cell_e1) / (
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
        definirion_e1_array = np.asarray([float(0) for x in range(len(p_array_1))])  # e1_array[1] - e1_array[0]
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

        Action_main = np.concatenate(
            (action_none_value, action_loadstage, action_wait, action_Stabilization, action_list))

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

        Deviator_kPa_main = np.around(
            np.concatenate((Deviator_kPa_none_value, Deviator_kPa_loadstage, Deviator_kPa_wait,
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

        VerticalPress_kPa_none_value = np.around(np.asarray(VerticalPress_kPa_none_value), decimals=1)

        VerticalPress_kPa_loadstage = np.around(np.asarray(VerticalPress_kPa_loadstage), decimals=1)

        VerticalPress_kPa_wait = np.around(np.asarray(VerticalPress_kPa_wait), decimals=1)

        VerticalPress_kPa_Stabilization = np.around(np.asarray(VerticalPress_kPa_Stabilization), decimals=1)

        np.around(VerticalPress_kPa, decimals=1)

        VerticalPress_kPa_main = np.around(
            np.concatenate((VerticalPress_kPa_none_value, VerticalPress_kPa_loadstage, VerticalPress_kPa_wait,
                            VerticalPress_kPa_Stabilization, VerticalPress_kPa)), decimals=1)

        # VerticalDeformation_mm
        # VerticalDeformation_mm
        # VerticalDeformation_mm
        VerticalDeformation_mm_none_value = np.around(np.asarray(VerticalDeformation_mm_none_value), decimals=4)

        VerticalDeformation_mm_loadstage = np.around(np.asarray(VerticalDeformation_mm_loadstage), decimals=4)

        VerticalDeformation_mm_wait = np.around(np.asarray(VerticalDeformation_mm_wait), decimals=4)

        VerticalDeformation_mm_Stabilization = np.around(np.asarray(VerticalDeformation_mm_Stabilization), decimals=4)

        e1_array = np.around(e1_array, decimals=4)

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

        VolumeStrain_main = np.around(
            np.concatenate((VolumeStrain_none_value, VolumeStrain_loadstage, VolumeStrain_wait,
                            VolumeStrain_Stabilization, VolumeStrain_list)), decimals=4)

        # VolumeDeformation_cm3
        # VolumeDeformation_cm3
        # VolumeDeformation_cm3
        VolumeDeformation_cm3_none_value = np.around(np.asarray(VolumeDeformation_cm3_none_value), decimals=3)

        VolumeDeformation_cm3_loadstage = np.around(np.asarray(VolumeDeformation_cm3_loadstage), decimals=3)

        VolumeDeformation_cm3_wait = np.around(np.asarray(VolumeDeformation_cm3_wait), decimals=3)

        VolumeDeformation_cm3_Stabilization = np.around(np.asarray(VolumeDeformation_cm3_Stabilization), decimals=3)

        ev_array_1 = np.around(ev_array_1, decimals=4)

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

        Deviator_MPa = np.around(Deviator_MPa, decimals=4)

        Deviator_MPa_main = np.around(
            np.concatenate((Deviator_MPa_none_value, Deviator_MPa_loadstage, Deviator_MPa_wait,
                            Deviator_MPa_Stabilization, Deviator_MPa)), decimals=4)

        # CellPress_MPa
        # CellPress_MPa
        # CellPress_MPa
        CellPress_MPa_none_value = np.around(np.asarray(CellPress_MPa_none_value), decimals=4)

        CellPress_MPa_loadstage = np.around(np.asarray(CellPress_MPa_loadstage), decimals=4)

        CellPress_MPa_wait = np.around(np.asarray(CellPress_MPa_wait), decimals=4)

        CellPress_MPa_Stabilization = np.around(np.asarray(CellPress_MPa_Stabilization), decimals=4)

        press_list = np.around(press_list, decimals=4)

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
                               f"{round(time_loadstage[-1] + random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation')), 1)} с.	")

        random_time_log = randint(40, 60) / 100
        log_Execute.setdefault(7,
                               f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(parametr_d.get('reconsolidation')), 1)} с.	{True}	")
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

        log_Execute.setdefault(18,
                               f"{round(time_wait[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(end_point_time_stab), 1)} с.		")

        random_time_log = -randint(40, 60) / 100
        log_Execute.setdefault(19,
                               f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Начато ожидание времени {round(float(end_point_time_stab), 1)} с.	{True}	")

        log_Execute.setdefault(20,
                               f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Ожидание времени завершено.		")

        volume_log_Stabilization = (volume_log_wait * 1000 + VolumeDeformation_cm3_Stabilization[-1]) / 1000
        vertical_log_Stabilization = (vertical_log_wait - VerticalDeformation_mm_Stabilization[-1])
        square_log_Stabilization = ((volume_log_wait * 1000) / vertical_log_wait) / 100

        random_time_log = -randint(30, 39) / 100
        log_Execute.setdefault(21,
                               f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Ожидание времени завершено.	{True}	")

        log_Execute.setdefault(22,
                               f"{round(time_Stabilization[-1] - random_time_log, 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.		")

        log_Execute.setdefault(23,
                               f"{round(time_list[-1], 2)}	Стадия: [Wait] Ожидание времени уплотнения; Сообщение: Размеры образца после дополнительного уплотнения составили: Высота {round(vertical_log_Stabilization, 2)} мм; Площадь {round(square_log_Stabilization, 1)} кв.см; Объем {round(volume_log_Stabilization, 1)} куб.см.	{True}	")

        log_Execute.setdefault(24,
                               f"{round(time_list[-1], 2)}	Стадия: [TerminateCondition] Испытание завершилось по условию; Сообщение: Завершения испытания...		")

        # перевод прочности в сm3 вместо mm3

        list_1000_vol = np.asarray([float(1000) for x in range(len(VolumeDeformation_cm3_main))])
        VolumeDeformation_cm3_main = VolumeDeformation_cm3_main / list_1000_vol

        # Time	Action	Action_Changed	Deviator_kPa	CellPress_kPa	VerticalPress_kPa	VerticalDeformation_mm	VerticalStrain	VolumeStrain	VolumeDeformation_cm3	Deviator_MPa	CellPress_MPa	VerticalPress_MPa	Trajectory
        # 14
        log_General.setdefault(0,
                               f"SampleHeight_mm	SampleDiameter_mm	SampleHeightConsolidated_mm	SampleVolumeConsolidated_cm3	SampleAreaConsolidated_cm2	PlungerArea_mm2	")
        log_General.setdefault(1, f"76	38	0.00	0.0000	0.0000	314	")
        log_General.setdefault(2, f"76	38	76.00	86.1490	11.3354	314	")
        log_General.setdefault(3,
                               f"76	38	{round(float(vertical_log_wait), 2)}	{round(float(volume_log_wait), 4)}	{11.3354}	314	")
        log_General.setdefault(4,
                               f"76	38	{round(float(vertical_log_Stabilization), 2)}	{round(float(volume_log_Stabilization), 4)}	{round(float(square_log_Stabilization), 4)}	314	")

        df = pd.DataFrame({'Time': Time_main, 'Action': Action_main, 'Action_Changed': Action_Changed_main,
                           'Deviator_kPa': Deviator_kPa_main, 'CellPress_kPa': CellPress_kPa_main,
                           'VerticalPress_kPa': VerticalPress_kPa_main,
                           'VerticalDeformation_mm': VerticalDeformation_mm_main,
                           'VerticalStrain': VerticalStrain_main, 'VolumeStrain': VolumeStrain_main,
                           'VolumeDeformation_cm3': VolumeDeformation_cm3_main,
                           'Deviator_MPa': Deviator_MPa_main,
                           'CellPress_MPa': CellPress_MPa_main, 'VerticalPress_MPa': VerticalPress_MPa_main,
                           'Trajectory': Trajectory_main})

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
        with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press) + '/Execute/' + 'Execute.1.log'}",
                  "w") as file:
            for key in log_Execute.keys():
                file.write(str(log_Execute.get(key)) + '\n')
        os.chdir('..')

        os.mkdir('General')
        os.chdir('General')

        with open(fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPS/' + str(press) + '/General/' + 'General.1.log'}",
                  "w") as file:
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

        p_array_1 = ((e1_array / (((((point_2_list_e1) ** (1 / 2)) - ((point_1_list_e1) ** (1 / 2))) / (
                    E_list * (point_2_list_otn_def - point_1_list_otn_def))) ** 2)) ** (1 / 2)) + press_list

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
        k_press_P = np.arange(press + point_press, press + point_press + quantity_point * search_P, search_P)

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


    def write_EngGeo_TPD(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance, list_choise,
                         list_choise_NU_tpd,
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


    def ISP_TPD(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_press, parametr_proba, parametr_d, points_l,
                picture_time):
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

        CellPress_kPa_wait = np.asarray(
            [float(CellPress_kPa_loadstage[-1]) for x in range(count_point_wait)]) - np.asarray(
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

        Action_main = np.concatenate(
            (action_none_value, action_loadstage, action_wait, action_Stabilization, action_list))

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

        Deviator_kPa_main = np.around(
            np.concatenate((Deviator_kPa_none_value, Deviator_kPa_loadstage, Deviator_kPa_wait,
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

        VolumeStrain_main = np.around(
            np.concatenate((VolumeStrain_none_value, VolumeStrain_loadstage, VolumeStrain_wait,
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

        Deviator_MPa_main = np.around(
            np.concatenate((Deviator_MPa_none_value, Deviator_MPa_loadstage, Deviator_MPa_wait,
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
        os.rename(f"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/obr_TPD.xml'}",
                  f"{File_Path + parametr_isp.get('LAB_NO')}/TPD/{picture_time}" + f"/{picture_time}.xml")

        os.mkdir('Execute')
        os.chdir('Execute')
        with open(
                fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/Execute/' + 'Execute.1.log'}",
                "w") as file:
            for key in log_Execute.keys():
                file.write(str(log_Execute.get(key)) + '\n')
        os.chdir('..')

        os.mkdir('General')
        os.chdir('General')
        with open(
                fr"{File_Path + parametr_isp.get('LAB_NO') + '/TPD/' + str(picture_time) + '/General/' + 'General.1.log'}",
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
            write_1 = (
                'INSERT INTO PROBAGR_PLOTNGR (OBJID, ZAMER_NO, DATA_ISP, RING_OBJID, VES0, VES1, VOL,ROP) VALUES ('
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
                           'VerticalPress_kPa': press_spd * 100, 'ePress_kPa': ePress_kPa,
                           'VerticalDeformation_mm': p_y,
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


    def write_SPS(cursor, SHEAR_DEF, T, TANGENT_PRESS, ZAMER_NUM, parametr_press, press, st, quantity_point,
                  SDDATA_OBJID):
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

        for x in range(len(SHEAR_DEF)-min_arr):
            SHEAR_DEF = np.delete(SHEAR_DEF, len(SHEAR_DEF) - 1)

        for x in range(len(T)-min_arr):
            T = np.delete(T, len(T) - 1)

        for x in range(len(TANGENT_PRESS)-min_arr):
            TANGENT_PRESS = np.delete(TANGENT_PRESS, len(TANGENT_PRESS) - 1)


        action_list = [str('Stabilization') for x in range(len(SHEAR_DEF))]

        action_changed_list = [str(True) for x in range(len(SHEAR_DEF))]

        press_sps = [float(parametr_press.get(press)) for x in range(len(SHEAR_DEF))]

        empty_list = [str('') for x in range(len(SHEAR_DEF))]

        name = [str('Срез') for x in range(len(SHEAR_DEF))]

        if len(TANGENT_PRESS) > len(SHEAR_DEF):
            TANGENT_PRESS = np.delete(TANGENT_PRESS, len(TANGENT_PRESS) - 1)

        df = pd.DataFrame({'Time': T, 'Action': action_list, 'Action_Changed': action_changed_list,
                           'VerticalPress_kPa': empty_list, 'ShearDeformation_mm': SHEAR_DEF,
                           'ShearPress_kPa': empty_list,
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
                                           0.002, 0.001, 0.0005]

                vertical_speed_rzg_now = vertical_speed_rzg_list.index(vertical_speed_rzg)

                try:
                    vertical_speed_rzg = vertical_speed_rzg_list[vertical_speed_rzg_now + 1]
                except:
                    print('Невозможно')

                return graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba,
                                  vertical_point_uploading)

            press = parametr_press.get('press')
            E = parametr_isp.get('E')

            e1_array = np.arange(0.000001, 11.4, vertical_speed_rzg)

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

            c_1 = last_point_1 / (math.atan(((e1_array_first[-1] / curve_test_min)) ** 0.5)) - press / (
                math.atan(((e1_array_first[-1] / curve_test_min)) ** 0.5))

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

            if point_1 == None or point_2 == None:
                vertical_point_uploading += 0.005

                return graph_tpdl(parametr_press, parametr_isp, vertical_speed_rzg, parametr_proba,
                                  vertical_point_uploading)

            E_now = round(list_module_max[point_1], 2)

            E_now_past = round(list_module_max[point_1], 2)

            count = 0

            E = round(E, 2)

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




                # print(count,'--',E_now,'--',LAB_NO,f"Нужно:{E}")



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

            press_2 = ((last_point_2 * math.atan((e1_array_second[0] / curve) ** 0.5)) / (
                        math.atan((e1_array_second[0] / curve) ** 0.5) - math.atan(
                    (e1_array_second[-1] / curve) ** 0.5))) - (last_point_1 / (((math.atan(
                (e1_array_second[0] / curve) ** 0.5)) / (math.atan((e1_array_second[-1] / curve) ** 0.5))) - 1))

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

                if parametr_proba.get('grunt_type') == 'gravel_sand' or parametr_proba.get(
                        'grunt_type') == 'large_sand':
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

        p_array_1, e1_array, points_l, otn_def, index_vertical_point_uploading = graph_tpdl(parametr_press,
                                                                                            parametr_isp,
                                                                                            vertical_speed_rzg,
                                                                                            parametr_proba,
                                                                                            parametr_d.get(
                                                                                                'vertical_point_uploading'))

        quantity_point = len(p_array_1)

        ev_array_1 = create_ev_tpdl(parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press, e1_array,
                                    otn_def,
                                    points_l[0], points_l[1])

        # дополнительный devisor от давления
        press = parametr_press.get('press')

        def summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, parametr_press, quantity_point, points_l,
                            parametr_isp,
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
                E2_right = parametr_isp.get('E2')
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

            line_1_e1 = np.arange(e1_array[search_point] - definition_e1 * quantity_point_line_1,
                                  e1_array[search_point],
                                  (definition_e1 * quantity_point_line_1) / quantity_point_line_1)

            Erzg_real_now = (line_1_p[search + 1] - line_1_p[search]) / (
                    ((line_1_e1[search + 1] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))) - (
                    (line_1_e1[search] - e1_array[0]) / (76 - abs(e1_array[1] - e1_array[0]))))

            # линия для EV
            line_1_EV = np.arange(ev_array_1[search_point], ev_array_1[search_point] + 100,
                                  +(100) / quantity_point_line_1)
            line_2_EV = np.arange(ev_array_1[search_point] - 100, ev_array_1[search_point],
                                  (100) / quantity_point_line_2)

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

        p_array_1, e1_array, ev_array_1 = summ_dop_line_1(otn_def, p_array_1, e1_array, ev_array_1, parametr_press,
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
                               'CellPress_MPa': press_list, 'VerticalPress_MPa': p_array_1,
                               'Trajectory': Trajectory_list})

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

                p_array_1, quantity_point, e1_array, otn_def = graph_tps(st, press, press_name, parametr_d,
                                                                         parametr_isp, vert_speed_tps, parametr_proba,
                                                                         random_start_e1)
                list_choise = list_choise1_tps(quantity_point, p_array_1)
                list_sequance = list_sequance1_tps(quantity_point)
                ev_array_1 = create_ev_tps(tps_parametr.get('b'), quantity_point, e1_array)
                if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
                    write_EngGeo_TPS(p_array_1, e1_array, ev_array_1, list_sequance, list_choise, EXAM_NUM, press,
                                     quantity_point, CM3DATA_OBJID)
                if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                        'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
                    ISP_TPS(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_proba, press, parametr_d,
                            parametr_press, vert_speed_tps, random_start_e1, otn_def)

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

            ev_array_1 = create_ev(otn_def, parametr_tpd.get('b'), quantity_point, parametr_proba, parametr_press,
                                   e1_array,
                                   points_l[0], points_l[1])

            picture_time = time.strftime("%Y.%m.%d %H_%M_%S", time.localtime(time.time()))
            if parametr_d.get('not_create_ISP') == 1 or parametr_d.get('write_and_createISP') == 1:
                write_EngGeo_TPD(parametr_press, p_array_1, e1_array, ev_array_1, list_sequance1, list_choise1,
                                 list_choise_NU_1, CM3DATA_OBJID)
            if parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                    'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1:
                ISP_TPD(p_array_1, e1_array, ev_array_1, parametr_isp, parametr_press, parametr_proba, parametr_d,
                        points_l, picture_time)

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

    # limiter - ограничитель
    try:

        limiter = 1

        parametr_isp = make_parametr_isp(isp_data, limiter)




        count_rows_df = len(isp_data)
        for update_lab in range(1, count_rows_df):

            if update_lab >= count_rows_df:
                break

            parametr_isp = make_parametr_isp(isp_data, update_lab)



            if (parametr_d.get('not_write_EngGeo') == 1 or parametr_d.get(
                    'not_write_EngGeo_not_EngGeo_parametr') == 1 or parametr_d.get('write_and_createISP') == 1) and (parametr_isp.get('TPS') != None or parametr_isp.get('TPD') !=  None or parametr_isp.get(
                    'SPS') !=  None or parametr_isp.get('TPDL') !=  None or parametr_isp.get('SPD') !=  None):
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

            if update_lab == 1:
                delete_parametr_one_time(parametr_d, parametr_isp, cursor)

            if parametr_isp.get('TPS') == None and parametr_isp.get('TPD') == None and parametr_isp.get(
                    'SPS') == None and parametr_isp.get('TPDL') == None and parametr_isp.get('SPD') == None:
                update_lab += 1

                if update_lab >= count_rows_df:
                    break

                continue



            parametr_proba = getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor, update_lab, isp_data)

            # удаление механики в пробе
            delete_parametr_many_time(parametr_d, parametr_isp, parametr_proba, cursor)

            execute_parametr_isp(parametr_d, parametr_proba, parametr_isp, cursor)

            parametr_press = calculate_press_gost(parametr_isp, parametr_proba, parametr_d)

            control_isp(parametr_isp, log_dict, parametr_d, parametr_proba, parametr_press, cursor)

            print(parametr_isp.get('LAB_NO'))

        cursor.commit()
        cursor.close()

        print(datetime.now() - start_time)
        print('Запись механики завершена')

        Di = input()

    except Exception as err:
        print('Исправляй  ' + parametr_isp.get('LAB_NO'))
        logging.exception(err)
        Di = input()



except Exception as err:

    logging.exception(err)

    Di = input()

