from random import randint

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