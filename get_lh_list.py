from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("mainwindow_lh.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
LH_URI = r'https://jeonse.lh.or.kr/jw/rs/search/reSearchRthousList.do?currPage='

setHouseInfo = {
    'mi': '2872', 
    'rthousBdtyp': '9',
    'rthousRentStle' : '9',
    'rthousDelngSttus' : '9',
    'rthousRoomCo' : '-1',
    'rthousToiletCo' : '-1',
    'northEast': '(37.563168390019136, 127.1907369136917)',
    'southWest': '(37.47681474463716, 127.05195750904815)',
    #광진구~강동구 근처?
    'rthousGtnFrom': '0',
    'rthousGtnTo': '12000'
}


def SelectTable(conn):
    cur = conn.cursor()
    cur.execute("SELECT rthousId FROM result")

    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

def CreateTable():
    conn = sqlite3.connect('LH.db')
    try:
        conn.execute('''CREATE TABLE RESULT(
            brkrNm text,
            brkrgComments text,
            confmAt text,
            mberAdres text,
            mberNm text,
            rsn text,
            rthousAllFloor text,
            rthousBdtyp text,
            rthousDelngSttus text,
            rthousExclAr text,
            rthousFakeSale text,
            rthousFloor text,
            rthousGtn text,
            rthousHppr text,
            rthousId text PRIMARY KEY,
            rthousInfoProvdTy text,
            rthousLnmAdres text,
            rthousLnmAdresDetail text,
            rthousLreaId text,
            rthousManagect text,
            rthousMberMbtlnum text,
            rthousMberMbtlnumOrigin text,
            rthousMberTelno text,
            rthousMberTelnoOrigin text,
            rthousMtht text,
            rthousNm text,
            rthousRdnmadr text,
            rthousRdnmadrDetail text,
            rthousRentStle text,
            rthousRgsde text,
            rthousRoomCo text,
            rthousSumryDc text,
            rthousSumryKwrd text,
            rthousToiletCo text,
            rthousXcnts text,
            rthousYdnts text,
            telno text,
            rthousSumrySj text,
            rthousInfoProvdLink text
            )
        ''')
    except sqlite3.OperationalError:
        print("테이블 있거나 에러~!")

    return conn

def InsertData(conn, fields, values):
    # pprint(str(values)[1:-1])
    try:
        conn.execute("INSERT INTO RESULT(" + fields[:-1]+ ")VALUES(" + str(values)[1:-1]+")")
        print("INSERT DONE")
        conn.commit()
    except sqlite3.IntegrityError:
        print("DUPLICATED OR ERROR")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    
    conn = CreateTable()

    for i in range(1, 100):
        html = requests.post(LH_URI + str(i), setHouseInfo)

        try:
            json_data = html.json()

        except json.decoder.JSONDecodeError:
            print("JSON invalid Error")
            break

        for detail in json_data["rthousList"]:
            InsertFields = dict()
            fields = str()
            values = list()

            for key in detail.keys():
                InsertFields[key] = detail[key]

                if key == 'rthousRgsde':
                    dttm = datetime.strptime(InsertFields[key], '%b %d, %Y %I:%M:%S %p')
                    fields += (key + ',')
                    values.append(str(dttm))

                else:
                    fields += (key + ',')
                    values.append(str(InsertFields[key]))

            InsertData(conn, fields, values)

    SelectTable(conn)
