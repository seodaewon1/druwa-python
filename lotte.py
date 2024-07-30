from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver import ActionChains
import time
import pandas as pd

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"lotte/lotte_{current_date}.json"

# ChromeOptions 객체 생성
chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")  # UI 모드에서 실행해 보기
chrome_options.add_argument("--no-sandbox")  # 샌드박스 사용 안 함
chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용 안 함
chrome_options.add_argument("--disable-gpu")  # GPU 사용 안 함
chrome_options.add_argument("--remote-debugging-port=9222")  # 디버깅 포트 설정
chrome_options.add_argument("--disable-software-rasterizer")  # 소프트웨어 렌더러 비활성화

# ChromeDriver 경로 설정
try:
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print(f"Error initializing WebDriver: {e}")
    exit(1)

keyword = '롯데리아 DT점'
url = f'https://map.naver.com/p/search/{keyword}'
print(f"Accessing URL: {url}")
driver.get(url)
action = ActionChains(driver)

naver_res = pd.DataFrame(columns=['title', 'address'])
last_name = ''

def search_iframe():
    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
        print("Switched to search iframe")
    except Exception as e:
        print(f"Error switching to search iframe: {e}")

def entry_iframe():
    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))
        print("Switched to entry iframe")
    except Exception as e:
        print(f"Error switching to entry iframe: {e}")

def chk_names():
    try:
        search_iframe()
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.place_bluelink')))
        elem = driver.find_elements(By.CSS_SELECTOR, '.place_bluelink')
        name_list = [e.text for e in elem]
        print(f"Names found: {name_list}")
        return elem, name_list
    except Exception as e:
        print(f"Error checking names: {e}")
        return [], []

def crawling_main(elem, name_list):
    global naver_res
    addr_list = []

    for e in elem:
        try:
            e.click()
            time.sleep(5)  # 페이지 로드 시간을 기다림
            entry_iframe()
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # append data
            try:
                addr_list.append(soup.select('span.LDgIH')[0].text)
            except IndexError:
                addr_list.append(float('nan'))

            search_iframe()
        except Exception as ex:
            print(f"Error during main crawling: {ex}")

    naver_temp = pd.DataFrame({
       'title': name_list,
        'address': addr_list
    })
    naver_res = pd.concat([naver_res, naver_temp])

def save_to_json():
    naver_res.to_json(filename, orient='records', force_ascii=False, indent=4)
    print(f"Data saved to {filename}")

page_num = 1

while True:
    time.sleep(10)
    elem, name_list = chk_names()

    if not name_list:
        print("이름 리스트가 비어 있습니다.")
        break

    if last_name == name_list[-1]:
        break

    while True:
        try:
            action.move_to_element(elem[-1]).perform()
            time.sleep(2)  # 이동 후 잠시 대기
            elem, name_list = chk_names()

            if not name_list or last_name == name_list[-1]:
                break
            else:
                last_name = name_list[-1]
        except Exception as e:
            print(f"Error during scrolling: {e}")
            break

    crawling_main(elem, name_list)

    # next page
    try:
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="eUTV2" and .//span[@class="place_blind" and text()="다음페이지"]]')))
        if next_button:
            next_button.click()
            print(f"{page_num} 페이지 완료")
            page_num += 1
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'place_bluelink')))
        else:
            print("마지막 페이지에 도달했습니다.")
            break
    except Exception as e:
        print(f"Error finding or clicking the next button: {e}")
        break

# JSON 파일로 저장
save_to_json()

# 브라우저 종료
driver.quit()
