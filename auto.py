from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ocr import ocr
from customException import CustomException
import time

TIMEOUT = 1
IMG_NAME = 'captcha.png'
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

def clickDate(d):
    # li:nth-child(d) 1달 중 해당 일의 위치
    # target 21
    css = '#themeCalendar > div > div:nth-child(3) > ul:nth-child(3) > li:nth-child(' + str(d) + ')'
    dateBtn = driver.find_element(By.CSS_SELECTOR, css)

    # 해당 일이 선택 가능한 상태인지 확인
    if "disabled" in dateBtn.get_attribute("class"):
        return False
    dateBtn.click()
    return True

def openBrowser(waitTime):
    able = False
    ### prod ###
    d = 21

    while not able:
        url = 'http://www.roomlescape.com/home.php?go=rev.make&themeSeq=6'
        driver.get(url)
        able = clickDate(d)
        time.sleep(waitTime)
    print(time.strftime('%Y-%m-%d %H:%M:%S'), end=" ")
    print("예약 가능 상태 확인")
    driver.maximize_window()

def selectTimeZone(hope):
    timeZones = driver.find_element(By.CSS_SELECTOR, '#themeTimeList').find_elements(By.TAG_NAME, 'li')

    for timeZone in reversed(timeZones):
        if timeZone.text not in hope:
            continue

        able = timeZone.get_attribute('class')
        if "impossible" in able:
            print("impossible " + timeZone.text)
            continue
        timeZone.click()
        return True
    return False

def keyIn(name, phone, person):
    board = driver.find_element(By.CSS_SELECTOR, '#tblForm')
    wait = WebDriverWait(board, TIMEOUT)
    cName = wait.until(EC.element_to_be_clickable((By.NAME, 'p_customerName')))
    cPhone = wait.until(EC.element_to_be_clickable((By.NAME, 'p_customerPhone')))
    cPerson = wait.until(EC.element_to_be_clickable((By.NAME, 'p_customerCnt')))
    captcha = wait.until(EC.element_to_be_clickable((By.NAME, 'ct_captcha')))

    imgCaptcha = board.find_element(By.CSS_SELECTOR, 'tbody > tr:nth-child(9) > th')
    imgCaptcha.screenshot(IMG_NAME)

    ### OCR
    strCaptcha = ocr(IMG_NAME, True)

    cName.send_keys(name)
    cPhone.send_keys(phone)
    cPerson.send_keys(person)
    captcha.send_keys(strCaptcha)

    cAgree = driver.find_element(By.CSS_SELECTOR, '#rev_agree > input[type=radio]:nth-child(2)')
    cAgree.click()

def submit():
    submitBtn = driver.find_element(By.CSS_SELECTOR, '#but_exe')
    submitBtn.click()

    alert = WebDriverWait(driver, TIMEOUT).until(EC.alert_is_present())
    alert.accept()

    try:
        alert = WebDriverWait(driver, TIMEOUT).until(EC.alert_is_present())
        msg = alert.text
        if '보안코드' in msg:
            alert.accept()
            raise CustomException('보안코드 인식 실패')
        return True

    except CustomException as e:
        print(e)
        return False

def auto():
    retry = False

    while not retry:
        openBrowser(0.5)


        ### timezone 설정 ###
        result = selectTimeZone({'13:50', '12:20', '09:20'})
        if not result:
            driver.close()
            return

        e = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#tblForm > tbody > tr:nth-child(9) > th > img')))
        keyIn('고윤제', '01012345678', str(3))

        ### prod 환경 (제출) ###
        retry = submit()
        ### test 환경 ###
        # retry = True

    print('----------------')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), end=" ")
    print("예약 성공!!")