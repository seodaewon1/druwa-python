from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"ceoban/ceoban_{current_date}.json"

# 웹드라이버 설정
options = ChromeOptions()
options.add_argument("--headless")  # 화면 출력 없이 실행
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)

# 웹 페이지 열기
browser.get('https://coffeebanhada.com/main/store/find.php?page_now=0&page_row=10&page_num=10&sido=&gugun=&keyword=&s_type4=7#res')

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "box2"))
)

# 페이지 소스 가져오기
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
ceoban_data = []

# tbody 내의 모든 tr 요소 선택
tracks = soup.select("tbody tr")

for track in tracks:
    tds = track.select("td")
    if len(tds) > 1:
        second_td = tds[1].text.strip()
        third_td = tds[2].text.strip()

        # 이미지 URL 추출 (수정 필요)
        image_element = track.select_one("img")  # tr 내에서 img 요소 선택
        image_url = image_element['src'] if image_element else None

        ceoban_data.append({
            "title": second_td,
            "address": third_td,
            "img": image_url
        })

# 데이터 확인
print(ceoban_data)

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(ceoban_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
