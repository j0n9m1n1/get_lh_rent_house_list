import time
from datetime import datetime
#Jun 10, 2020 4:09:43 PM
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
teststr = "brkrNm, brkrgComments, confmAt, mberAdres, mberNm, rsn, rthousAllFloor, rthousBdtyp, rthousDelngSttus, rthousExclAr, rthousFakeSale, rthousFloor, rthousGtn, rthousHppr, rthousId, rthousInfoProvdTy, rthousLnmAdres, rthousLnmAdresDetail, rthousLreaId, rthousManagect, rthousMberMbtlnum, rthousMberMbtlnumOrigin, rthousMberTelno, rthousMberTelnoOrigin, rthousMtht, rthousNm, rthousRdnmadr, rthousRdnmadrDetail, rthousRentStle, rthousRgsde, rthousRoomCo, rthousSumryDc, rthousSumryKwrd, rthousToiletCo, rthousXcnts, rthousYdnts, telno, rthousSumrySj, rthousInfoProvdLink,"
dttm = "Jun 10, 2020 4:09:43 PM"
# datetime.month("Jun")
# print(datetime.ctime("Jun 10, 2020 4:09:43 PM"))

timeStr = '2018-07-28 12:11:32'
timeStr = 'Jun 10, 2020 4:09:43 PM'
Thistime = datetime.strptime(timeStr, '%b %d, %Y %I:%M:%S %p')
print(Thistime)