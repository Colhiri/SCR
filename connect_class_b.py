import sys
from gspread import service_account_from_dict, exceptions
from pyodbc import connect, Error
import configparser

# NewAccess_Enggeo = cc.ConnectAccess() - create new object
# connect_EGE = NewAccess_Enggeo.connect_bd() - new connect_bd
# cursor_EGE = NewAccess_Enggeo.cursor_bd() - new cursor_bd
# ==========================================================
# NewConnect = cc.ConnectTable()  #create new object from googlesheet
# NewConnect.connect_to_googlesheet(object_name) #create connect to object_name
# worksheet_journal = NewConnect.connect_to_spreadsheet('LIST')


def load_path_to_bd_from_comfig():
    config = configparser.ConfigParser()
    try:
        config.read("settings.ini")
        config_conn_bd = config["access_connect"]["path_bd"]
        return config_conn_bd
    except (KeyError, Error):
        input('[path_bb] not found / edit settings.ini and press [Enter]')
        return load_path_to_bd_from_comfig()


class ConnectTable:
    def __init__(self):
        self.google_sheets_connect = None
        self.google_key_connect = None
        self.lolka = {
  "type": "service_account",
  "project_id": "skkk-373717",
  "private_key_id": "7c38f28ab88ec273e416b220cc2b8827b3a6a5d6",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDWifVcqXWwxhkE\nqiWol8VFftarhg2s5oX7ieZjSQSY7LMFfv2B2UKYQPgVIa6u8Usdft/6qOSLnXUP\nuxI5sNK2S+aexxFs0m+fAftnFxnk8boRZOfr8fLloKmMq/u/0zNasnfacxUrNOXG\n3L3hJzpwO0Ky8rPryPISvdJFyjJytAxgiaok9k4z6LVllFWnoCmo1kwbV9vHiH8r\nKkFoAf8c0DJ/tBu6K7oqXPItPgnV76iqjNGcDXkVF6kMnyn8fYGEQtFQ5a/gWC+T\n6Km97L8UuIlC/Rs1Lf2CPrtY3HEw2cf70Rj0N5dL4E1cL5DWk7Pi7XweY5xhhokR\nqSMazUz1AgMBAAECggEAAxZDGI07q0p+a6nDFvTwGrrjfd5U7gr3HJJ0ZTNUxJqL\nTOXx4d9tbOFqcGtmpw/Dw+3ibSnm9/dRCuPnNDtOHN9ktx4oKwewIXqW0nnrnna3\n9a4dBDEcDJ/OML78xVrVn1V4EgWb5V5CfCUK+mVlGt5PbGG/owHmMczXbLenGC1m\nTFzhpRBCETjR15aAKcvdhprTG6GHm6UFgN1CIu6h9Mhy8fcsytmcZxeIda+TKuB5\ncMRSPceMro3UMH0dlXJXZfLPbzamL0YY2GGk5ljsIXN2xr9PKodoWeA1xf6FO0es\nnrzo/YSpSkympvXwfSE9V/H4IkBoO89oUPYoOlWqYQKBgQDzng6waqyk8eKaD3wc\nnB9+Z5PmrYgh9DJu/h1UKFcKVzSBoZQnq+O4KZj8a/p4fogGlmXjPcKQXRdNI8JS\nuadmrWyn/d9IOestfbJhZFYsHObjjwUtfGvHEC4/60E0d9+Ft/97YBFOcK6dD37k\nV9/iy8X1szXpZvtpWrmJ0p+5mQKBgQDhcYhGkd1OugvKU47srhuX2kaL2sVYUawU\njPIM9Z46KAsRq96YBPERSUQ3qehkbPLQKe9G121C0eycbyjVesfCQo4d6nwd1H/6\noIfrghYJgDV87K7s84NDZj0ZXt31YQupCqpTWZsSB3XXf0uQPipSiIutc3KFlWGN\n1TZm7P3fvQKBgC992I87vHxLS0mNSzyoktsphgOqQKed21cX4s/NLWqupWXAAgnZ\n0ILOWSycQC/NOudN2n76QzuxaiF3nyJRXvj9RflZ3HVQFTDBGE00KjhfSgOClhfP\n8ZLU7K85RXTdCY4f2IZMrBMGlIO5yZrqJpMn9md3kEL3+HsJXLIphUnBAoGBAIRB\nZW/4/HrF/Eq60FsbHQbtv3smYaWZbDk2In3lzehSO4QnbtOB+qZodAOvwqy/mYbz\nQvMtSGTt4EA5mhv7Bpt5DgSQ3jVlx5qReIt56lGyjC54b3qEtRniLa/njpD4WK3X\nmuqA488k30YH4J2DSrLWdhLQanvhkbRyQ5MILzuFAoGACWxuLGVTXDalxg/sllav\nG9PxBcM+FdWNqMffVcHp5gFdSJ4S0CCygR/iYahDuNm+L2GHcGsC9vwgo7K0GiiH\nqa5jjyRl/7tiQGi6d+3pa7DA1FLMLnlqSMZXmYqus9fxWQI8ss78emsVl6MqDoLT\nFm9nZ5997SgzMkDxZNVrOwE=\n-----END PRIVATE KEY-----\n",
  "client_email": "skkk-235@skkk-373717.iam.gserviceaccount.com",
  "client_id": "117002049306086450957",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/skkk-235%40skkk-373717.iam.gserviceaccount.com"
}


    def connect_to_googlesheet(self, object_name):
        print(f'..google connection to object : | {object_name} |')
        self.google_key_connect = service_account_from_dict(self.lolka)
        try:
            self.google_sheets_connect = self.google_key_connect.open(
                object_name)
            print(f'[connected] to [file]: |{object_name}| - [connected]')
            return self.google_sheets_connect
        except (exceptions.SpreadsheetNotFound,):
            print('..the connection : Error[!] SpreadsheetNotFound[!]:')
            object_name = input('\t|||repeat input: ')
            return self.connect_to_googlesheet(object_name)

    def connect_to_spreadsheet(self, sheet_name):
        try:
            worksheet = self.google_sheets_connect.worksheet(sheet_name)
            print(f'\r..[connected] to [sheet] : {sheet_name}.')
            return worksheet
        except exceptions.WorksheetNotFound:
            print(f'\r..error google connection to sheet {sheet_name} !')
        except AttributeError:
            input('AttributeError [!] - destructed sheet / reload ')
            sys.exit()


class ConnectAccess:
    DRIVER = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'

    def __init__(self):
        self.ENGGEO_BD = None
        self.access_path = None
        self.conn = None

    def connect_bd(self):
        try:
            self.access_path = load_path_to_bd_from_comfig()
            self.ENGGEO_BD = f'DBQ={self.access_path}'
            self.conn = connect(f'{self.DRIVER}\n{self.ENGGEO_BD}')
            print(f'{self.access_path} [connected to access]')
            return self.conn
        except Error:
            input('%s    [pyodbc.Error - name!]' % self.access_path)
            self.access_path = load_path_to_bd_from_comfig()
            return self.connect_bd()

    def cursor_bd(self):
        try:
            curs = self.conn.cursor()
            return curs
        except Error:
            pass
        except AttributeError:
            pass



