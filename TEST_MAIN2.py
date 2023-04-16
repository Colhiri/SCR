import datetime

import pandas as pd

import extract02_t
import pyodbc

#input name object
object = input('Объект:'    )

path = r'C:\Users\MSI GP66\Desktop\HETA_base\HETA.mdb'

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + path + '')
cursor = conn.cursor()

test = extract02_t.ObjectUnload(object)
object_dict = {}
for skv, probs in test.request_skv_probes().items():
    for prob in probs:
        w0 = test.extract_data_probagr('PROBAGR_W', prob, 0)
        if w0 == []:
            continue


        probagr = test.extract_probagr(skv, prob)
        probagr_ln = [p[2] for p in probagr]
        # print(probagr_ln)
        w0 = test.extract_data_probagr('PROBAGR_W', prob, 0)
        w1 = test.extract_data_probagr('PROBAGR_W', prob, 1)
        ro0 = test.extract_data_probagr_ro(prob)
        wl0 = test.extract_data_probagr('PROBAGR_WL', prob, 0)
        wl1 = test.extract_data_probagr('PROBAGR_WL', prob, 1)
        wp0 = test.extract_data_probagr('PROBAGR_WP', prob, 0)
        gss = test.extract_data_probagr_gss(prob)
        #
        #
        #
        #
        #
        select_prgr = "SELECT OBJID, PROBAGR_OBJID FROM SVODKA_TBL WHERE PROBAGR_OBJID = ?"
        result_search = cursor.execute(select_prgr, prob).fetchall()
        result_search = list(result_search[0])
        PROBEGR_SVODKA = result_search[0]

        select_prgr = "SELECT OBJID, Ip, IL, Sr, Kpor, Ro, W, RoS FROM SVODKA_FIZMEX WHERE OBJID = ?"
        result_search = cursor.execute(select_prgr, PROBEGR_SVODKA).fetchall()
        result_search = list(result_search[0])
        Ip = result_search[1]
        IL = result_search[2]
        Sr = result_search[3]
        Kpor = result_search[4]
        Ro = result_search[5]
        W = result_search[6]
        RoS = result_search[7]

        if Ip == None:
            consistency = None
            water_saturation = None
            IL = None
            main_type = 'incoherent'  # несвязный
            #
            #
            # VES1, GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01
            try:
                GGR10 = gss[0][1]
                G10_5 = gss[0][2]
                G5_2 = gss[0][3]
                G2_1 = gss[0][4]
                G1_05 = gss[0][5]
                G05_025 = gss[0][6]
                G025_01 = gss[0][7]
            except:
                continue

            #
            fraction_grans = [GGR10, G10_5, G5_2, G2_1, G1_05, G05_025, G025_01]
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





        object_dict[probagr_ln[0]] = {
            'probagr': probagr,
            'w0': w0,
            'w1': w1,
            'ro0': ro0,
            'wl0': wl0,
            'wl1': wl1,
            'wp0': wp0,
            'gss': gss,
            'Main': Main_type,
            'Second':Type_disp}



new_dict = {}
space1 = ''
for probagr in object_dict.values():
    print(probagr)
    skv, depth_ot, lab_num = probagr['probagr'][0]
    depth_ot = round(depth_ot, 2)
    print(skv, depth_ot, lab_num)
    if len(probagr['w0']) != 0:
        bucs_w0, wet_w0, dry_w0 = probagr['w0'][0]
        wet_w0, dry_w0 = round(wet_w0, 2), round(dry_w0, 2)
    else:
        bucs_w0, wet_w0, dry_w0 = '', '', ''
    if len(probagr['w1']) != 0:
        bucs_w1, wet_w1, dry_w1 = probagr['w1'][0]
        wet_w1, dry_w1 = round(wet_w1, 2), round(dry_w1, 2)
    else:
        bucs_w1, wet_w1, dry_w1 = '', '', ''
    if len(probagr['ro0']) != 0:
        ring_num, soil_weight = probagr['ro0'][0]
        soil_weight = round(soil_weight, 2)
    else:
        ring_num, soil_weight = '', ''
    if len(probagr['wl0']) != 0:
        bucs_wl0, wet_wl0, dry_wl0 = probagr['wl0'][0]
        wet_wl0, dry_wl0 = round(wet_wl0, 2), round(dry_wl0, 2)
    else:
        bucs_wl0, wet_wl0, dry_wl0 = '', '', ''
    if len(probagr['wl1']) != 0:
        bucs_wl1, wet_wl1, dry_wl1 = probagr['wl1'][0]
        wet_wl1, dry_wl1 = round(wet_wl1, 2), round(dry_wl1, 2)
    else:
        bucs_wl1, wet_wl1, dry_wl1 = '', '', ''
    if len(probagr['wp0']) != 0:
        bucs_wp0, wet_wp0, dry_wp0 = probagr['wp0'][0]
        wet_wp0, dry_wp0 = round(wet_wp0, 2), round(dry_wp0, 2)
    else:
        bucs_wp0, wet_wp0, dry_wp0 = '', '', ''
    try:
        vesgss, a10, a5, a2, a1, a05, a025, a01 = probagr['gss'][0]
        vesgss, a10, a5, a2, a1, a05, a025, a01 = round(vesgss, 2), round(a10, 2), round(a5, 2), round(a2, 2), round(a1, 2), round(a05, 2), round(a025, 2), round(a01, 2)
    except:
        vesgss, a10, a5, a2, a1, a05, a025, a01 = '', '', '', '', \
                                                  '', '', '', ''

    Main_type = probagr['Main']
    Type_disp = probagr['Second']


    new_dict[lab_num] = [skv, depth_ot, lab_num,
                         bucs_w0, wet_w0, dry_w0,
                         bucs_w1, wet_w1, dry_w1,
                         ring_num, soil_weight,
                         bucs_wl0, wet_wl0, dry_wl0,
                         bucs_wl1, wet_wl1, dry_wl1,
                         bucs_wp0, wet_wp0, dry_wp0,
                         vesgss, a10, a5, a2, a1, a05, a025, a01, Main_type, Type_disp]
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
    24: "a1", 25: "a05", 26: "a025", 27: "a01", 28: "Грунт", 29: "Тип"
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



df[har_list] = df[har_list].astype("float64", errors= 'ignore')
df[har_list] = df[har_list].round(2)
df[har_list] = df[har_list].astype("str")
df[har_list] = df[har_list].stack().str.replace('.', ',', regex=True).unstack()
df.fillna(' ')
sorted_df = df.sort_values(by='lab_num')
sorted_df = sorted_df.transpose()
sorted_df.dropna()



print(sorted_df)
print(sorted_df.info())
sorted_df.to_csv(f"{object}.log", sep='\t', index=False, header=False)
