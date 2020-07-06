import pickle
from pprint import pprint
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
LH_URI = r'https://jeonse.lh.or.kr/jw/rs/search/reSearchRthousList.do?currPage='
'''
values에 따옴표 씌워줘야함
'''
addrData = {
    'mi': '2872', 
    'rthousBdtyp': '9',
    'rthousRentStle' : '9',
    'rthousDelngSttus' : '9',
    'rthousRoomCo' : '-1',
    'rthousToiletCo' : '-1',
    'northEast': '(37.563168390019136, 127.1907369136917)',
    'southWest': '(37.47681474463716, 127.05195750904815)',
    'rthousGtnFrom': '0',
    'rthousGtnTo': '12000'
}
months = {
    'Jan' : '1',
    'Feb' : '2',
    'Mar' : '3',
    'Apr' : '4',
    'May' : '5',
    'Jun' : '6',
    'Jul' : '7',
    'Aug' : '8',
    'Sep' : '9',
    'Oct' : '10',
    'Nov' : '11',
    'Dec' : '12'
}
def InitDict():
    InsertFields = {
    'brkrNm' : '',
    'brkrgComments': '',
    'confmAt':'',
    'mberAdres':'',
    'mberNm':'',
    'rsn':'',
    'rthousAllFloor':'',
    'rthousBdtyp':'',
    'rthousDelngSttus':'',
    'rthousExclAr':'',
    'rthousFakeSale':'',
    'rthousFloor':'',
    'rthousGtn':'',
    'rthousHppr':'',
    'rthousId':'',
    'rthousInfoProvdTy':'',
    'rthousLnmAdres':'',
    'rthousLnmAdresDetail':'',
    'rthousLreaId':'',
    'rthousManagect':'',
    'rthousMberMbtlnum':'',
    'rthousMberMbtlnumOrigin':'',
    'rthousMberTelno':'',
    'rthousMberTelnoOrigin':'',
    'rthousMtht':'',
    'rthousNm':'',
    'rthousRdnmadr':'',
    'rthousRdnmadrDetail':'',
    'rthousRentStle':'',
    'rthousRgsde':'',
    'rthousRoomCo':'',
    'rthousSumryDc':'',
    'rthousSumryKwrd':'',
    'rthousToiletCo':'',
    'rthousXcnts':'',
    'rthousYdnts':'',
    'telno':''
    }

    return InsertFields

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
    # print("INSERT INTO RESULT(" + fields[:-1]+ ")VALUES(" + str(values)[1:-1]+")")
    try:
        conn.execute("INSERT INTO RESULT(" + fields[:-1]+ ")VALUES(" + str(values)[1:-1]+")")
        print("INSERT DONE")
        conn.commit()
    except sqlite3.IntegrityError:
        print("duplicated")

if __name__ == "__main__":
    
    conn = CreateTable()
    #광진구~강동구 근처?
    test = 1
    #방 100개가 안 됨
    if test == 1:
        for i in range(1, 10):
            html = requests.post(LH_URI + str(i), addrData)
            try:
                json_data = html.json()
            except json.decoder.JSONDecodeError:
                print("JSON invalid Error")
            #방 없으면 break
            if len(json_data["rthousList"]) <= 0: break
            #있으면 돌고
            else:   
                fields = str()
                values = list()
                for detail in json_data["rthousList"]:
                    InsertFields = InitDict()
                    for keys in detail.keys():
                        InsertFields[keys] = detail[keys]
                    #7이 제일 많음 37
                    
                    # pprint(InsertFields)
                    for key in InsertFields.keys():
                        if key is 'rthousRgsde':
                            print("key is rthousRgsde: " + str(InsertFields[key]))
                            dttm = datetime.strptime(InsertFields[key], '%b %d, %Y %I:%M:%S %p')
                            print(dttm)

                            fields += (key + ',')
                            values.append(str(dttm))
                        else:
                            fields += (key + ',')
                            values.append(str(InsertFields[key]))
                            # print(values)

                    InsertData(conn, fields, values)
