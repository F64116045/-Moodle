from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
import cv2
import os


pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  

driver = webdriver.Chrome()
driver.get('https://moodle.ncku.edu.tw/') 

try:
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
    

    username.send_keys('F64116045')  
    password.send_keys('password')  # 在這輸password

    retry_attempts = 3

    for attempt in range(retry_attempts):
        captcha_image = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="imgcode"]')))
        captcha_image.screenshot('captcha.png')

        image = cv2.imread('captcha.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # 保存處理後的圖片(檢查用)
        cv2.imwrite('processed_captcha.png', thresh)
        print("處理後的驗證碼圖片已保存: processed_captcha.png")

        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        captcha_text = pytesseract.image_to_string(thresh, config=custom_config).strip()

        print(f"Tesseract 辨識出的驗證碼是: {captcha_text}")

        # 檢查辨識結果的長度
        if len(captcha_text) == 4 and captcha_text.isdigit():
            # 填寫驗證碼
            captcha_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'vcode')))
            captcha_input.send_keys(captcha_text)

            # 提交表單
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Log in"]')))
            submit_button.click()
            break  
        else:
            print(f"辨識失敗，重新獲取驗證碼（嘗試次數: {attempt + 1}/{retry_attempts}）")

    else:
        print("無法辨識，請手動輸入。")

except Exception as e:
    print(f"發生錯誤: {e}")
finally:
    input("任意鍵關閉...") 
    driver.quit()
