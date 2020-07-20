#출처: https://www.inflearn.com/questions/22997
'''

villa base url: https://apis.zigbang.com/v2/items?deposit_lteq=15000&domain=zigbang&geohash=wydmk&new_villa=true&sales_type_in=%EC%A0%84%EC%84%B8&zoom=15
deposit_lteq: 15000
domain: zigbang
geohash: wydmk
new_villa: true
sales_type_in: 전세
zoom: 15
one room base url: https://apis.zigbang.com/v2/items?deposit_gteq=0&deposit_lteq=9000&domain=zigbang&geohash=wydm7&rent_gteq=0&sales_type_in=%EC%A0%84%EC%84%B8%7C%EC%9B%94%EC%84%B8&service_type_eq=%EC%9B%90%EB%A3%B8
deposit_gteq: 0
deposit_lteq: 9000
domain: zigbang
geohash: wydm7
rent_gteq: 0
sales_type_in: 전세|월세
service_type_eq: 원룸
'''
'''
2020-01-29 직방 사이트 리뉴얼로 인해 내부 ajax 통신 방식 변경으로 인한 수정
기존에 사용하던 직방 내부의 api 는 사용되지 않습니다.
Geohash 를 사용하기 위해서

pip install geohash2

라이브러리를 설치해야 합니다.
'''
import requests
import pprint
import geohash2

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
    url = "https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang&geohash={}&rent_gteq=0&sales_type_in=전세%7C월세&service_type_eq=원룸".format(geohash)

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