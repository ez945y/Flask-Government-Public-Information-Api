from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from time import sleep
import datetime

header = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
ser = Service('.\chromedriver.exe')
op = webdriver.ChromeOptions()
op.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
op.add_experimental_option('useAutomationExtension', False)
op.add_experimental_option("detach", True)
op.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})

def waitXpath(xpath, driver):
    locator = (By.XPATH, xpath)
    WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))


if __name__ == "__main__":
    driver=webdriver.Chrome(service=ser,options=op)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
    """
    })
    driver.maximize_window()
    driver.get('https://webpro.twse.com.tw/WebPortal/vod/101/?categoryId=101')
    try:
        for i in range(0,3):
            res_url = []
            driver.implicitly_wait(20)
            sleep(3)
            for url in driver.find_elements(By.CLASS_NAME,'DIV_ScreenShot'):
                res_url.append(url.find_element(By.CSS_SELECTOR,'a').get_attribute('href')+"\n")
            driver.find_element("xpath",'//*[@id="arrow_right"]').click()
            
            with open('webURL.txt','r',encoding="utf-8") as f:
                a = f.readlines()
                a.extend(res_url)
            with open('webURL.txt','w',encoding="utf-8") as f:
                f.writelines(a)
                
        driver.close()
    except Exception as e:
        print(e)

