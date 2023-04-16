import connect_class_b as cc
from random import randint

NewAccess_Enggeo = cc.ConnectAccess()
connect_EGE = NewAccess_Enggeo.connect_bd()
cursor_EGE = NewAccess_Enggeo.cursor_bd()




class ObjectUnload:
    def __init__(self, object_name):
        self.object_name = object_name

    def request_skv_probes(self):
        cod_list = []
        request = cursor_EGE.execute(
            # f"SELECT OBJID "
            # f"FROM PROBAGR "
            # f"WHERE COD = ("
            f"SELECT SK_OBJID "
            f"FROM SK_PER_OBJECT "
            f"WHERE WOBJ_OBJID = ("
            f"SELECT OBJID "
            f"FROM WOBJECT "
            f"WHERE NAMEOBJ_SHORT = '{self.object_name}')")
        cod_skv_list = [val[0] for val in request.fetchall()]
        for cod in cod_skv_list:
            request = cursor_EGE.execute(
                f"SELECT OBJID "
                f"FROM PROBAGR "
                f"WHERE COD = '{cod}'")
            cod_proba_list = \
                cod_list.append([val[0] for val in request.fetchall()])
        fm_dict = dict(zip(cod_skv_list, cod_list))
        print(fm_dict)
        return fm_dict

    def extract_probagr(self, objid_skv, objid_prob):
        req_skv = (
            f"SELECT N_SKV "
            f"FROM SK "
            f"WHERE OBJID = '{objid_skv}'")
        request = cursor_EGE.execute(
            f"SELECT ({req_skv}) ,GLUB_OT, LAB_NO "
            f"FROM PROBAGR "
            f"WHERE OBJID = '{objid_prob}'")
        result = [list(val) for val in request.fetchall()]
        print(result)
        return result



    def extract_data_probagr(self, sheet_name, objid_prob, zamer):
        def bucs_sel(sheet_name, objid_prob):
            bucs_select = cursor_EGE.execute(
                f"SELECT num "
                f"FROM Bucs "
                f"WHERE P IN ("
                    f"SELECT VES0 " 
                    f"FROM {sheet_name} "
                    f"WHERE OBJID = '{objid_prob}' AND ZAMER_NO = {zamer})")
            try:
                bucs_found = bucs_select.fetchone()[0]
            except TypeError:
                bucs_found = randint(1, 10)
            print(f'bucs!! == {bucs_found}')
            return bucs_found

        request = cursor_EGE.execute(
            f"SELECT ({bucs_sel(sheet_name, objid_prob)}), VES_VLGR, VES_SHGR "
            f"FROM {sheet_name} "
            f"WHERE OBJID = '{objid_prob}' AND ZAMER_NO = {zamer}")
        # result = request.fetchall()
        result = [list(val) for val in request.fetchall()]
        print(result)
        return result

    def extract_data_probagr_ro(self, objid_prob):
        ring_select = cursor_EGE.execute(
            f"SELECT NUM "
            f"FROM Rings "
            f"WHERE P IN ("
                f"SELECT ROUND (VES0,2) "
                f"FROM PROBAGR_PLOTNGR "
                f"WHERE OBJID = '{objid_prob}')")
        try:
            ring_found = ring_select.fetchone()[0]
        except TypeError:
            ring_found = randint(1, 10)
        print(ring_found)
        request = cursor_EGE.execute(
            f"SELECT ({ring_found}), VES1 "
            f"FROM PROBAGR_PLOTNGR "
            f"WHERE OBJID = '{objid_prob}'")
        # result = request.fetchall()
        result = [list(val) for val in request.fetchall()]
        result = [val for val in result]
        print(result)
        return result

    def extract_data_probagr_gss(self, objid_prob):
        request = cursor_EGE.execute(
            f"SELECT VES1, GGR10, G10_5, G5_2 ,G2_1, G1_05, G05_025, G025_01 "
            f"FROM PROBAGR_GRANSOST "
            f"WHERE OBJID = '{objid_prob}'")
        result = [list(val) for val in request.fetchall()]
        # result = request.fetchall()
        print(result)
        return result
