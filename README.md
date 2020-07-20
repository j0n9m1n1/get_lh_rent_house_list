# get_lh_rent_house_list
https://jeonse.lh.or.kr/jw/rs/search/selectRthousList.do?mi=2871#wrap

기존의 LH에서 제공하는 페이지는 filter 없음, 본거 또 보고 내리고 계속 해야함
내려서 2페이지 누르면 2페이지 맨 아래부터 다시 위로 올려야함

전세임대 포털의 설정한 지도 영역만큼의 매물 가져오기

1. 검색 필드 만들기(등록일, 금액, 관리비)
2. 체크박스로 관리비 5만원 이상인 data 색 강조하기
3. 옆에 지도 넣기
    - 지도 top_left, bottom_right 좌표로 row 더블클릭시 위치 표시 or 5번
4. 가져온 데이터에 해당하는 LH링크 연결해주기
5. table row dblClick시 Widget 팝업으로 정보 보여주기
6. 메뉴를 통해 특정 영역 지정하기(현재는 내가 쓰려고 광진, 송파, 사당쪽만 넣어둠)
7. 직방, 다방 탭으로 추가하기()


pip install requests, pyqt5
pip install PyQtWebEngine



