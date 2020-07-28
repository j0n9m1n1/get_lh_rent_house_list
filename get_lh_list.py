import time
from pprint import pprint
import sqlite3
from datetime import datetime
import requests
import json
import sys
import geohash2
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import webbrowser

'''
매물 상세보기 url POST
param은 rthousId
https://jeonse.lh.or.kr/jw/rs/search/selectRthousInfo.do?rthousId=b0e228af3420443ea3e1204dfad049aa
'''
setHouseLHInfo = {
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
setHouseZBInfo = {
    "keyword": "아차산"
}

LH_URL = r"https://jeonse.lh.or.kr/jw/rs/search/reSearchRthousList.do?currPage="
LH_DETAIL = r"https://jeonse.lh.or.kr/jw/rs/search/selectRthousInfo.do?rthousId="
ZB_URL = "https://apis.zigbang.com/search?q={}".format(setHouseZBInfo["keyword"])
form_class = uic.loadUiType("mainwindow_lh.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.conn = sqlite3.connect("rooms.db")
        # LH Data Table 생성
        self.CreateTableLH()
        self.CreateTableZB()
        self.InitLHDB()

        self.tableWidget_LH.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.btn_search_LH.clicked.connect(self.ClickedSearchBtnLH)
        self.btn_search_ZB.clicked.connect(self.ClickedSearchBtnZB)
        self.btn_webSearch.clicked.connect(self.ClickedWebSearchBtn)
        self.tableWidget_LH.doubleClicked.connect(self.dblClickedTableRowLH)

    def ClickedSearchBtnLH(self):
        '''
        검색 조건 추가 시~
        startDate = 0
        endDate = 0
        grtMoney = 0
        '''
        print(self.cbBox_Location.currentText())
        self.InitLHDB()
        while (self.tableWidget_LH.rowCount() > 0):
            self.tableWidget_LH.removeRow(0)
        self.SetItemsLH()

    def ClickedSearchBtnZB(self):
        self.InitZBDB()
        self.SetItemsZB()

    def CreateTableLH(self):
        conn = self.conn
        try:
            conn.execute(
                """CREATE TABLE LH(
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
            print("LH: 테이블 있거나 에러~!", end='')
            print(sqlite3.OperationalError)

    def CreateTableZB(self):
        conn = self.conn
        try:
            conn.execute(
                """CREATE TABLE ZB(
                search_keyword text,
                address text,
                address1 text,
                address2 text,
                address3 text,
                building_floor text,
                deposit text,
                floor text,
                floor_string text,
                images_thumbnail text,
                is_first_movein text,
                is_new text,
                is_zzim text,
                item_id text PRIMARY KEY,
                manage_cost text,
                random_location_lat text,
                random_location_lng text,
                reg_date text,
                rent text,
                room_type text,
                room_type_title text,
                sales_title text,
                sales_type text,
                section_type text,
                service_type text,
                size_m2 text,
                status text,
                tags text,
                title text,
                contract_size_m2 text,
                contract_size_p text,
                supply_size_m2 text,
                supply_size_p text,
                own_size_m2 text,
                own_size_p text,
                detail_desc text)
                """)
        except sqlite3.OperationalError:
            print("ZB: 테이블 있거나 에러~!", end='')
            print(sqlite3.OperationalError)

    def CreateTableDB(self):
        pass

    def InsertDataLH(self, fields, values):
        conn = self.conn
        # pprint(str(values)[1:-1])
        try:
            conn.execute(
                "INSERT INTO LH("
                + fields[:-1]
                + ")VALUES("
                + str(values)[1:-1]
                + ")"
            )
            print("LH: INSERT DONE")
            conn.commit()
        except sqlite3.IntegrityError:
            print("LH: DUPLICATED OR ERROR")

    def InsertDataZB(self, fields, values):
        conn = self.conn
        # print(str(values)[1:-1])
        print(str(fields)[1:-1])
        print(str(values)[1:-1])
        try:
            conn.execute(
                "INSERT INTO ZB("
                + str(fields)[1:-1]
                + ")VALUES("
                + str(values)[1:-1]
                + ")"
            )
            print("ZB: INSERT DONE")
            conn.commit()
        except sqlite3.IntegrityError:
            print("ZB: DUPLICATED OR ERROR")

    def InsertDataDB(self):
        pass

    def InitLHDB(self):
        for i in range(1, 5):
            html = requests.post(LH_URL + str(i), setHouseLHInfo[self.cbBox_Location.currentText()])

            try:
                json_data = html.json()

            except json.decoder.JSONDecodeError:
                print("JSON invalid Error")
                break

            for detail in json_data["rthousList"]:
                insert_fields = dict()
                fields = str()
                values = list()

                for key in detail.keys():
                    insert_fields[key] = detail[key]

                    if key == "rthousRgsde":
                        _dttm = datetime.strptime(
                            insert_fields[key], "%b %d, %Y %I:%M:%S %p"
                        )
                        fields += key + ","
                        values.append(str(_dttm))

                    else:
                        fields += key + ","
                        values.append(str(insert_fields[key]))
                # print(str(i) + ": ", end="")
                self.InsertDataLH(fields, values)

    def InitZBDB(self):
        keyword = self.lineEdit_ZB.text()
        url = "https://apis.zigbang.com/search?q={}".format(keyword)
        req = requests.get(url)
        _json = req.json()
        if _json.get("code") == "200":
            data = _json.get("items")[0]
            # pprint(data)
            _description = data.get("description")
            _id = data.get("id")
            _lat = data.get("lat")
            _lng = data.get("lng")
            _zoom = data.get("zoom")

            geohash = geohash2.encode(_lat, _lng, precision=5)
            # 여기까지는 키워드의 itemid, 좌표 구하는거

            url = "https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang&geohash={}&rent_gteq=0&sales_type_in=전세%7C월세&service_type_eq=원룸".format(
                geohash)
            _req_items = requests.get(url).json()
            _items = _req_items.get("items")

            item_ids = []
            for item in _items:
                item_ids.append(item.get("item_id"))
            # 갯수 조정
            items = {"item_ids": item_ids[:100]}
            _results = requests.post('https://apis.zigbang.com/v2/items/list', data=items).json()
            _datas = _results.get("items")

            for dict in _datas:
                fields, values = list(), list()
                for dict_key in dict.keys():
                    if dict[dict_key] is not None:
                        if dict_key == "계약면적":
                            fields.append("contract_size_m2")
                            values.append(str(dict[dict_key]["m2"]))
                            fields.append("contract_size_p")
                            values.append(str(dict[dict_key]["p"]))

                        elif dict_key == "공급면적":
                            fields.append("supply_size_m2")
                            values.append(str(dict[dict_key]["m2"]))
                            fields.append("supply_size_p")
                            values.append(str(dict[dict_key]["p"]))

                        elif dict_key == "전용면적":
                            fields.append("own_size_m2")
                            values.append(str(dict[dict_key]["m2"]))
                            fields.append("own_size_p")
                            values.append(str(dict[dict_key]["p"]))

                        elif dict_key == "random_location":
                            fields.append("random_location_lat")
                            values.append(str(dict[dict_key]["lat"]))
                            fields.append("random_location_lng")
                            values.append(str(dict[dict_key]["lng"]))
                        else:
                            fields.append(dict_key)
                            values.append(str(dict[dict_key]))

                    else:
                        if dict_key == "계약면적":
                            fields.append("contract_size_m2")
                            values.append("-1")

                            fields.append("contract_size_p")
                            values.append("-1")
                        else:
                            fields.append(dict_key)
                            values.append("-1")
                    # print(dict_key, values)
                self.InsertDataZB(fields, values)

    def SetItemsLH(self):
        conn = self.conn
        cur = conn.cursor()

        cur.execute(
            "SELECT rthousRgsde, rthousRdnmadr , rthousRdnmadrDetail, rthousGtn, rthousMtht, rthousManagect, rthousFloor, rthousExclAr, rthousRoomCo, rthousToiletCo, rthousXcnts, rthousYdnts, rthousId FROM LH ORDER BY rthousRgsde DESC"
        )
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            rowCount = self.tableWidget_LH.rowCount()
            self.tableWidget_LH.setRowCount(rowCount + 1)
            # 등록일
            self.tableWidget_LH.setItem(rowCount, 0, QTableWidgetItem(str(row[0])))
            # 주소(지번) + 상세주소(지번)
            if row[2] == None:
                self.tableWidget_LH.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]))
                )
            else:
                self.tableWidget_LH.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]) + " " + str(row[2]))
                )
                # print(str(row[2]))
            # 보증금
            self.tableWidget_LH.setItem(rowCount, 2, QTableWidgetItem(str(row[3])))
            # 월세
            self.tableWidget_LH.setItem(rowCount, 3, QTableWidgetItem(str(row[4])))
            # 관리비
            self.tableWidget_LH.setItem(rowCount, 4, QTableWidgetItem(str(row[5])))
            # 면적
            self.tableWidget_LH.setItem(rowCount, 5, QTableWidgetItem(str(row[6])))
            # 층
            self.tableWidget_LH.setItem(rowCount, 6, QTableWidgetItem(str(row[7])))
            # 방
            self.tableWidget_LH.setItem(rowCount, 7, QTableWidgetItem(str(row[8])))
            # 화장실
            self.tableWidget_LH.setItem(rowCount, 8, QTableWidgetItem(str(row[9])))
            # X
            self.tableWidget_LH.setItem(rowCount, 9, QTableWidgetItem(str(row[10])))
            # Y
            self.tableWidget_LH.setItem(rowCount, 10, QTableWidgetItem(str(row[11])))
            # ID
            self.tableWidget_LH.setItem(rowCount, 11, QTableWidgetItem(str(row[12])))

            print(str(i) + ": " + str(row))

    def SetItemsZB(self):

        conn = self.conn
        cur = conn.cursor()

        cur.execute(
            "SELECT reg_date, address, address1, address2, address3, deposit, rent, manage_cost, floor, building_floor, size_m2, random_location_lng, random_location_lat, item_id FROM ZB ORDER BY reg_date DESC"
        )
        rows = cur.fetchall()
        for i, row in enumerate(rows):
            print(i, " ", row)
            rowCount = self.tableWidget_ZB.rowCount()
            self.tableWidget_ZB.setRowCount(rowCount + 1)
            # 등록일
            self.tableWidget_ZB.setItem(rowCount, 0, QTableWidgetItem(str(row[0])))
            # 주소(지번) + 상세주소(지번)
            if row[2] == None:
                self.tableWidget_ZB.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]))
                )
            else:
                self.tableWidget_ZB.setItem(
                    rowCount, 1, QTableWidgetItem(str(row[1]) + " " + str(row[2]))
                )
                # print(str(row[2]))
            # 보증금
            self.tableWidget_ZB.setItem(rowCount, 2, QTableWidgetItem(str(row[3])))
            # 월세
            self.tableWidget_ZB.setItem(rowCount, 3, QTableWidgetItem(str(row[4])))
            # 관리비
            self.tableWidget_ZB.setItem(rowCount, 4, QTableWidgetItem(str(row[5])))
            # 면적
            self.tableWidget_ZB.setItem(rowCount, 5, QTableWidgetItem(str(row[6])))
            # 층
            self.tableWidget_ZB.setItem(rowCount, 6, QTableWidgetItem(str(row[7])))
            # X
            self.tableWidget_ZB.setItem(rowCount, 7, QTableWidgetItem(str(row[8])))
            # Y
            self.tableWidget_ZB.setItem(rowCount, 8, QTableWidgetItem(str(row[9])))
            # ID
            self.tableWidget_ZB.setItem(rowCount, 9, QTableWidgetItem(str(row[10])))

            # print(str(i) + ": " + str(row))

    def ClickedWebSearchBtn(self):
        self.AddNewWebTab(QUrl(self.lineEdit_url.text()), 'Loading...')

    def RenewURLBar(self, qurl, browser):
        #없어도 무방함
        self.lineEdit_url.setText(qurl.toDisplayString())

    def AddNewWebTab(self, qurl, label='labels'):
        browser = QWebEngineView()
        webSettings = browser.settings()
        webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        browser.setUrl(qurl)

        i = self.tabWidget_map.addTab(browser, label)
        self.tabWidget_map.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.RenewURLBar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabWidget_map.setTabText(i, browser.page().title()))

    def dblClickedTableRowLH(self):
        x, y = self.tableWidget_LH.item(self.tableWidget_LH.currentRow(), 9).text(), self.tableWidget_LH.item(
            self.tableWidget_LH.currentRow(), 10).text()

        location_url = QUrl('https://www.google.com/maps/search/%s,%s' % (y, x))
        self.AddNewWebTab(location_url)

        detail_url = QUrl(LH_DETAIL + self.tableWidget_LH.item(
            self.tableWidget_LH.currentRow(), 11).text())
        self.AddNewWebTab(detail_url)

    def dblClickedTableRowZB(self):
        print("dblclickedZBTable")
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
