import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import tkinter as tk
from tkinter import ttk
import webbrowser

url = 'https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdPublishList.do'

headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

prodNmList = ['전시관','전시실','전시물','전시연출','전시 연출','전시기획','전시 기획','전시설계','전시 설계','전시환경','전시 환경','박물관','홍보관','홍보실','체험관','체험장','체험물','기념관','역사관','문학관','실감','미디어','미디어파사드', '미디어 파사드', '키즈카페', '키즈 카페', '실물모형', '실물 모형', '유니버', '범죄없는', '범죄 없는', '안전체험', '안전 체험', '조형물','경관']
taskClCdList = ['3']

base_form = {
  'taskClCd': '5',
  'orderbyItem': '1',
  'searchType': '1',
  'supplierLoginYn': 'N',
  'instCl': '2',
  'taskClCds': taskClCdList,
  'prodNm': '',
  'swbizTgYn': '',
  'searchDetailPrdnmNo': '',
  'searchDetailPrdnm': '',
  'fromRcptDt': '2024/11/25',
  'toRcptDt': '2024/12/25',
  'recordCountPerPage': '100'
}

forms = []
for prod_nm in prodNmList:
  form = base_form.copy()
  form['prodNm'] = prod_nm.encode('euc-kr')
  forms.append(form)

bid_list = []

for form in forms:
  res = requests.post(url, data = form)

  soup = BeautifulSoup(res.text, 'html.parser')
  rows = soup.find('tbody').find_all('tr')
  for row in rows:
    # td 태그들 찾기
    cols = row.find_all('td')
    if len(cols) < 6: continue
    
    # 필요한 정보 추출
    reg_no = cols[1].find('a').text.strip()  # 등록번호
    name = cols[3].find('a').text.strip()    # 품명
    org = cols[4].text.strip()               # 수요기관
    date = cols[5].text.strip()              # 사전규격공개일시
    budget = "정보없음"
    
    # 상세 페이지에서 price 정보 가져오기
    detail_url = f'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={reg_no}'
    detail_res = requests.get(detail_url)
    detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
    
    try:
        table = detail_soup.find('table', class_='table_info')
        budget = table.find_all('tr')[2].find_all('td')[0].find('div', class_='tb_inner').text.strip()
        budget = budget.replace('₩', '').strip()
    except:
        budget = "정보없음"
    
    bid_list.append([reg_no, name, org, date, budget])

# GUI 생성
root = tk.Tk()
root.title('입찰공고 목록')

# 창 크기 설정
window_width = 1200
window_height = 600
root.geometry(f'{window_width}x{window_height}')

# 화면 중앙에 위치시키기
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_width) / 2)
center_y = int((screen_height - window_height) / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# 전체 레코드 수 표시
total_label = tk.Label(root, text=f'총 {len(bid_list)}개의 공고가 검색되었습니다.', pady=10)
total_label.pack()

# Treeview 생성
display_columns = ['순번', '품명', '수요기관', '공개일시', '예산금액']
tree = ttk.Treeview(root, columns=display_columns, show='headings')

# 열 제목 설정과 너비 조정
column_widths = {
  '순번': 20,
  '품명': 300,
  '수요기관': 200,
  '공개일시': 150,
  '예산금액': 150
}

# 컬럼 설정
for col in display_columns:
  tree.heading(col, text=col)
  tree.column(col, width=column_widths[col])
  # 순번 열만 가운데 정렬
  if col == '순번':
    tree.column(col, anchor='center')

# 데이터 추가 (등록번호는 tree에 표시하지 않고 tags에 저장)
for idx, item in enumerate(bid_list, start=1):
  reg_no = item[0]  # 등록번호 저장
  display_values = [idx] + item[1:]  # 순번과 나머지 정보만 표시
  tree.insert('', 'end', values=display_values, tags=(reg_no,))  # 등록번호를 tags에 저장

# 클릭 이벤트 처리 함수
def on_tree_click(event):
  item = tree.selection()[0]
  reg_no = tree.item(item)['tags'][0]  # tags에서 등록번호 가져오기
  detail_url = f'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={reg_no}'
  webbrowser.open(detail_url)

# 더블클릭 이벤트 바인딩
tree.bind('<Double-1>', on_tree_click)

# 스크롤바 추가
scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(fill='both', expand=True, padx=10, pady=10)

# 창을 맨 앞으로 가져오기
root.update()
root.attributes('-topmost', True)
root.focus_force()
root.attributes('-topmost', False)  # 다시 False로 설정하여 다른 창을 앞으로 가져올 수 있게 함

root.mainloop()