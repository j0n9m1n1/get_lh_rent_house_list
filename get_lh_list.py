from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import sys

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

LH_URI = r"https://jeonse.lh.or.kr/jw/rs/search/reSearchRthousList.do?currPage="

setHouseInfo = {
    "GUNJA": {
        "mi": "2872",
        "rthousBdtyp": "9",
        "rthousRentStle": "9",
        "rthousDelngSttus": "9",
        "rthousRoomCo": "-1",
        "rthousToiletCo": "-1",
        "northEast": "(37.563168390019136, 127.1907369136917)",
        "southWest": "(37.47681474463716, 127.05195750904815)",
        "rthousGtnFrom": "0",
        "rthousGtnTo": "13000",
    },
    "SADANG": {

        "mi": "2872",
        "rthousBdtyp": "9",
        "rthousRentStle": "9",
        "rthousDelngSttus": "9",
        "rthousRoomCo": "-1",
        "rthousToiletCo": "-1",
        "northEast": "(37.50135006369378, 126.99113361405719)",
        "southWest": "(37.45806743112682, 126.90966927353564)",
        "rthousGtnFrom": "0",
        "rthousGtnTo": "13000",
    }
}

form_class = uic.loadUiType("mainwindow_lh.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.conn = sqlite3.connect("LH.db")

        self.InitDB()
        # self.SelectForTable()
        self.tableWidget_db.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabWidget.removeTab(1)
        self.tabWidget.removeTab(0)

        self.addNewTab(QUrl('https://map.google.com'))
        print("initDB Done")
        self.btn_search.clicked.connect(self.ClickedSearchBtn)
        self.btn_webSearch.clicked.connect(self.ClickedWebSearchBtn)
        self.tableWidget_db.doubleClicked.connect(self.coordinateToURL)

    def ClickedWebSearchBtn(self):
        self.addNewTab(QUrl(self.lineEdit_url.text()), 'Loading...')

    def ClickedSearchBtn(self):
        startDate = 0
        endDate = 0
        grtMoney = 0
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
            html = requests.post(LH_URI + str(i), setHouseInfo["SADANG"])

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

        cur.execute(
            "SELECT rthousRgsde, rthousRdnmadr , rthousRdnmadrDetail, rthousGtn, rthousMtht, rthousManagect, rthousFloor, rthousExclAr, rthousRoomCo, rthousToiletCo, rthousXcnts, rthousYdnts FROM result ORDER BY rthousRgsde DESC"
        )
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            rowCount = self.tableWidget_db.rowCount()
            self.tableWidget_db.setRowCount(rowCount + 1)
            # 등록일
            self.tableWidget_db.setItem(rowCount, 0, QTableWidgetItem(str(row[0])))
            # 주소(지번) + 상세주소(지번)
            if row[2] == None:
                self.tableWidget_db.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]))
                )
            else:
                self.tableWidget_db.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]) + " " + str(row[2]))
                )
                # print(str(row[2]))
            # 보증금
            self.tableWidget_db.setItem(rowCount, 2, QTableWidgetItem(str(row[3])))
            # 월세
            self.tableWidget_db.setItem(rowCount, 3, QTableWidgetItem(str(row[4])))
            # 관리비
            self.tableWidget_db.setItem(rowCount, 4, QTableWidgetItem(str(row[5])))
            # 면적
            self.tableWidget_db.setItem(rowCount, 5, QTableWidgetItem(str(row[6])))
            # 층
            self.tableWidget_db.setItem(rowCount, 6, QTableWidgetItem(str(row[7])))
            # 방
            self.tableWidget_db.setItem(rowCount, 7, QTableWidgetItem(str(row[8])))
            # 화장실
            self.tableWidget_db.setItem(rowCount, 8, QTableWidgetItem(str(row[9])))
            # X
            self.tableWidget_db.setItem(rowCount, 9, QTableWidgetItem(str(row[10])))
            # Y
            self.tableWidget_db.setItem(rowCount, 10, QTableWidgetItem(str(row[11])))

            print(str(i) + ": " + str(row))

    def renew_urlbar(self, qurl, browser):
        self.lineEdit_url.setText(qurl.toDisplayString())

    def addNewTab(self, qurl, label='labels'):
        browser = QWebEngineView()
        self.webSettings = browser.settings()
        self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        browser.setUrl(qurl)
        i = self.tabWidget.addTab(browser, label)

        self.tabWidget.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.renew_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabWidget.setTabText(i, browser.page().title()))

    def coordinateToURL(self):
        x, y = self.tableWidget_db.item(self.tableWidget_db.currentRow(), 9).text(), self.tableWidget_db.item(
            self.tableWidget_db.currentRow(), 10).text()
        print(x, y)
        location_url = QUrl('https://www.google.com/maps/@%s,%s,17z' % (y, x))
        self.addNewTab(location_url)


#

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
