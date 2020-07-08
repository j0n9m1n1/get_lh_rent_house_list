from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

LH_URI = r"https://jeonse.lh.or.kr/jw/rs/search/reSearchRthousList.do?currPage="

setHouseInfo = {
    "mi": "2872",
    "rthousBdtyp": "9",
    "rthousRentStle": "9",
    "rthousDelngSttus": "9",
    "rthousRoomCo": "-1",
    "rthousToiletCo": "-1",
    "northEast": "(37.563168390019136, 127.1907369136917)",
    "southWest": "(37.47681474463716, 127.05195750904815)",
    # 광진구~강동구 근처?
    "rthousGtnFrom": "0",
    "rthousGtnTo": "12000",
}


form_class = uic.loadUiType("mainwindow_lh.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        columnLabels = ["등록일", "주소", "보증금", "크기"]
        self.tableWidget_db.setColumnCount(10)
        self.tableWidget_db.setRowCount(10)
        self.tableWidget_db.setHorizontalHeaderLabels(columnLabels)

        self.conn = sqlite3.connect("LH.db")

        self.InitDB()
        self.SelectForTable()
        print("initDB Done")
        self.btn_search.clicked.connect(self.ClickedSearchBtn)

    def ClickedSearchBtn(self):

        self.SelectForTable()

    def CreateTable(self):
        conn = self.conn
        try:
            conn.execute(
                """CREATE TABLE RESULT(
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
            """
            )
        except sqlite3.OperationalError:
            print("테이블 있거나 에러~!")

    def InsertData(self, fields, values):
        conn = self.conn
        # pprint(str(values)[1:-1])
        try:
            conn.execute(
                "INSERT INTO RESULT("
                + fields[:-1]
                + ")VALUES("
                + str(values)[1:-1]
                + ")"
            )
            print("INSERT DONE")
            conn.commit()
        except sqlite3.IntegrityError:
            print("DUPLICATED OR ERROR")

    def InitDB(self):
        self.CreateTable()

        for i in range(1, 5):
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

                    if key == "rthousRgsde":
                        dttm = datetime.strptime(
                            InsertFields[key], "%b %d, %Y %I:%M:%S %p"
                        )
                        fields += key + ","
                        values.append(str(dttm))

                    else:
                        fields += key + ","
                        values.append(str(InsertFields[key]))
                print(str(i) + ": ", end="")
                self.InsertData(fields, values)

    def SelectForTable(self):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT rthousRgsde FROM result")
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            print(str(i) + ": " + str(row))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
