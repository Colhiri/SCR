def getting_parameters_from_enggeo(parametr_d, parametr_isp, cursor):
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

    # поиск значений пробы в сводке
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

    # основной тип грунта для механики
    if Ip == None:
        consistency = None
        water_saturation = None
        IL = None
        main_type = 'incoherent'  # несвязный
        # поиск грансостава пробы в сводке
        select_prgr = "SELECT OBJID,GGR10,G10_5,G5_2,G2_1,G1_05,G05_025,G025_01,G01_005 FROM SVODKA_GRANS WHERE OBJID = ?"
        result_search = cursor.execute(select_prgr, PROBEGR_SVODKA).fetchall()
        result_search = list(result_search[0])
        GGR10 = result_search[1]
        G10_5 = result_search[2]
        G5_2 = result_search[3]
        G2_1 = result_search[4]
        G1_05 = result_search[5]
        G05_025 = result_search[6]
        G025_01 = result_search[7]
        G01_005 = result_search[8]

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

    param_proba = ['PROBEGR_IDS', 'GLUB', 'PROBEGR_SVODKA', 'grunt_type', 'consistency', 'density', 'water_saturation',
                   'main_type', 'Ip', 'IL', 'Sr', 'Kpor', 'Ro', 'W', 'RoS', 'CMUSL_OBJID', 'parametr_write_temporary']
    param_proba_value = [PROBEGR_IDS, GLUB, PROBEGR_SVODKA, grunt_type, consistency, density, water_saturation,
                         main_type, Ip, IL, Sr, Kpor, Ro, W, RoS, CMUSL_OBJID, parametr_write_temporary]
    for parametr, value in zip(param_proba, param_proba_value):
        parametr_proba.setdefault(parametr, value)
    return parametr_proba