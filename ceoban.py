from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"ceoban/ceoban_{current_date}.json"

# 웹드라이버 설치
options = ChromeOptions()
options.add_argument("--headless")
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)

browser.get('https://coffeebanhada.com/main/store/find.php?page_now=0&page_row=10&page_num=10&sido=&gugun=&keyword=&s_type4=7#res')

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "box2"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
ceoban_data = []

# 첫 번째 tracks
tracks = soup.select("tbody tr")

for track in tracks:
    tds = track.select("td")
    if len(tds) > 1:  # 두 번째 td가 있는지 확인
        second_td = tds[1].text.strip()
        third_td = tds[2].text.strip()

            # 이미지 URL 추출
        image_element = soup.select_one(".fotorama__img")
        image_url = image_element.get('src') if image_element else None
        ceoban_data.append({
            "title": second_td,
            "address": third_td,
            "img": image_url
        })

print(ceoban_data)


print(ceoban_data)

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(ceoban_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
