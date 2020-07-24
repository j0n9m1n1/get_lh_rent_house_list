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
        self.InitDB()
        self.tableWidget_LH.setEditTriggers(QAbstractItemView.NoEditTriggers)
        print("initDB Done")
        self.btn_search_LH.clicked.connect(self.ClickedSearchBtnLH)
        self.btn_search_ZB.clicked.connect(self.ClickedSearchBtnZB)
        self.btn_webSearch.clicked.connect(self.ClickedWebSearchBtn)
        self.tableWidget_LH.doubleClicked.connect(self.dblClickedTableRow)

    def ClickedSearchBtnLH(self):
        '''
        검색 조건 추가 시~
        startDate = 0
        endDate = 0
        grtMoney = 0
        '''
        while (self.tableWidget_LH.rowCount() > 0):
            self.tableWidget_LH.removeRow(0)
        self.SetItemsLH()

    def ClickedSearchBtnZB(self):
        keyword = "아차산"

        # 최초 검색어에 해당하는 검색어값의 자동완성 ajax 주소 입니다.
        # 예를 들어 사이트에서 대치동을 입력하면 대치동, 르엘대치(아파트), 대치동더블유타워(오피스텔)... 등의
        # 검색 결과목록이 나오는데 이 값을 구해오는 주소 입니다.
        url = "https://apis.zigbang.com/search?q={}".format(keyword)

        req = requests.get(url)

        # 실제 api 주소에서 json 형태로 리턴되기 때문에 json 형태로 값을 받습니다.
        # json 형태로 받은 값은 사용하기도 편리합니다.
        _json = req.json()

        # api 상태코드가 200인 경우가 오류없이 동작되었다는 의미입니다.
        if _json.get("code") == "200":
            # 위에서 말한대로 검색어에 해당하는 자동완성값은 여러개인데
            # 그중에 맨 위에 [0] 번째 한가지에 대해서만 검색을 합니다.
            data = _json.get("items")[0]
            _description = data.get("description")
            _id = data.get("id")
            _lat = data.get("lat")
            _lng = data.get("lng")
            _zoom = data.get("zoom")

            # 기존코드와 현재 변경된 직방 페이지에서 가장 중요하게 변경된 점은
            # 기존에는 lat, lng 값을 구해서 임의로 적정 영역을 +, - 해서
            # 지도의 사각형 영역을 구한다음에 그 영역에 대한 쿼리를 요청했었는데
            # 변경된 직방 사이트는 Geohash 를 사용하도록 변경되었습니다.
            # Geohash 에 대한 정보는 https://en.wikipedia.org/wiki/Geohash 를 참고하시기 바랍니다.
            # 맨위에 설명한데로 파이썬 geohash2 라이브러를 먼저 설치해야 합니다.
            # precision 정밀도를 5로 설정해야만 직방에서 사용하는 geohash 와 일치하는듯 보입니다.
            geohash = geohash2.encode(_lat, _lng, precision=5)

            # 위에서 구한 geohash 값을 아래의 api 로 호출하고 쿼리(전세 월세 등)를 넘겨주는 주소 입니다.
            url = "https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang&geohash={}&rent_gteq=0&sales_type_in=전세%7C월세&service_type_eq=원룸".format(
                geohash)

            # 역시 json 형태로 값을 취합니다.
            _req_items = requests.get(url).json()

            # json 데이터에서 items 값만 저장합니다.
            # items 값은 실제 매물 데이터의 인덱스 값입니다.
            _items = _req_items.get("items")

            # 위에서 취한 json 형태의 items 목록을
            # 파이썬 리스트 형태로 저장합니다.
            item_ids = []
            for item in _items:
                item_ids.append(item.get("item_id"))

            # 위에서 저장한 list 의 100개만
            # items_ids 라는 키의 값으로 설정합니다.
            # 최종적으로 이 값을 직방 api 에 요청합니다.
            items = {"item_ids": item_ids[:100]}

            # 위에서 만든 items_ids: [매물인덱스] 를 아래 주소로 쿼리 한 후 json 형태로 받습니다.
            _results = requests.post('https://apis.zigbang.com/v2/items/list', data=items).json()

            # 최종 완성된 매물 결과는 items 안에 있습니다.
            datas = _results.get("items")

            # 매물 목록을 돌며 화면에 출력합니다.
            for d in datas:
                _address = "{} {}".format(d.get("address1"), d.get("address2"))
                if d.get("address3") is not None:
                    _address += " {}".format(d.get("address3"))

                building_floor = d.get("building_floor")
                floor = d.get("floor")
                thumbnail = d.get("images_thumbnail")
                item_id = d.get("item_id")
                reg_date = d.get("reg_date")
                sales_type = d.get("sales_type")
                service_type = d.get("service_type")
                size_m2 = d.get("size_m2")
                title = d.get("title")
                deposit = d.get("deposit")
                rent = d.get("rent")

                # pprint.pprint(d)
                print("*" * 100)
                print("{} [{}]".format(title, item_id))
                print("보증금/월세: {}/{}".format(deposit, rent))
                print("건물층/매물층: {}/{}".format(building_floor, floor))
                print("등록일자: {}".format(reg_date))
                print("서비스형태/매물형태: {}/{}".format(service_type, sales_type))
                print("사이즈: {}".format(size_m2))

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
            print("테이블 있거나 에러~!")

    def CreateTableZB(self):
        pass

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
            print("INSERT DONE")
            conn.commit()
        except sqlite3.IntegrityError:
            print("DUPLICATED OR ERROR")

    def InsertDataZB(self):
        pass

    def InsertDataDB(self):
        pass

    def InitDB(self):
        self.CreateTableLH()

        for i in range(1, 5):
            html = requests.post(LH_URL + str(i), setHouseLHInfo["GUNJA"])

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
                self.InsertDataLH(fields, values)

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

    def ClickedWebSearchBtn(self):
        self.AddNewWebTab(QUrl(self.lineEdit_url.text()), 'Loading...')

    def RenewURLBar(self, qurl, browser):
        self.lineEdit_url.setText(qurl.toDisplayString())

    def AddNewWebTab(self, qurl, label='labels'):
        browser = QWebEngineView()
        self.webSettings = browser.settings()
        self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        browser.setUrl(qurl)
        if ('rthousId' in str(qurl)):
            i = self.tabWidget_detail.addTab(browser, label)

            self.tabWidget_detail.setCurrentIndex(i)

            browser.urlChanged.connect(lambda qurl, browser=browser: self.RenewURLBar(qurl, browser))

            browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                         self.tabWidget_detail.setTabText(i, browser.page().title()))
        else:
            i = self.tabWidget_map.addTab(browser, label)

            self.tabWidget_map.setCurrentIndex(i)

            browser.urlChanged.connect(lambda qurl, browser=browser: self.RenewURLBar(qurl, browser))

            browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                         self.tabWidget_map.setTabText(i, browser.page().title()))

    def dblClickedTableRow(self):
        x, y = self.tableWidget_LH.item(self.tableWidget_LH.currentRow(), 9).text(), self.tableWidget_LH.item(
            self.tableWidget_LH.currentRow(), 10).text()
        print(x, y)
        location_url = QUrl('https://www.google.com/maps/search/%s,%s' % (y, x))
        self.AddNewWebTab(location_url)

        detail_url = QUrl(LH_DETAIL + self.tableWidget_LH.item(
            self.tableWidget_LH.currentRow(), 11).text())
        self.AddNewWebTab(detail_url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
