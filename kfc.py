# 현재 날짜 가져오기 
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"kfc/kfc_{current_date}.json"

# ChromeOptions 객체 생성
chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")  # 헤드리스 모드 사용
chrome_options.add_argument("--no-sandbox")  # 샌드박스 사용 안 함
chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용 안 함
chrome_options.add_argument("--disable-gpu")  # GPU 사용 안 함

# ChromeDriver 경로 설정
service = ChromeService(executable_path=ChromeDriverManager().install())

# WebDriver 객체 생성
driver = webdriver.Chrome(service=service, options=chrome_options)

keyword = 'KFC DT점'
url = f'https://map.naver.com/v5/search/{keyword}'
print(f"Accessing URL: {url}")
driver.get(url)
action = ActionChains(driver)

naver_res = pd.DataFrame(columns=['title', 'address'])
last_name = ''

# Save page source to file for analysis
with open('page_source.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)
print("Page source saved to page_source.html")

def search_iframe():
    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#searchIframe")))
        print("Switched to search iframe")
    except Exception as e:
        print(f"Error switching to search iframe: {e}")

def entry_iframe():
    try:
        driver.switch_to.default_content()
        WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#entryIframe")))
        print("Switched to entry iframe")
    except Exception as e:
        print(f"Error switching to entry iframe: {e}")

def chk_names():
    try:
        search_iframe()
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.place_bluelink')))
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
            entry_iframe()
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # append data
            try:
                addr_list.append(soup.select('span.LDgIH')[0].text)
            except IndexError:
                addr_list.append(float('nan'))

            search_iframe()
        except Exception as e:
            print(f"Error during main crawling: {e}")

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
    time.sleep(3)
    elem, name_list = chk_names()

    if not name_list:
        print("이름 리스트가 비어 있습니다.")
        break

    if last_name == name_list[-1]:
        break

    while True:
        try:
            action.move_to_element(elem[-1]).perform()
            time.sleep(3)
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
        next_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="eUTV2" and .//span[@class="place_blind" and text()="다음페이지"]]')))
        if next_button:
            next_button.click()
            print(f"{page_num} 페이지 완료")
            page_num += 1
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'place_bluelink')))
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
