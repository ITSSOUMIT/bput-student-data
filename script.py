from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import sys

stdoutOrigin=sys.stdout 
sys.stdout = open("log.txt", "w")

def scrap(usernameinp, passwordinp):
    # Create a new instance of the Chrome driver

    # headless chrome
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    # gui chrome
    # driver = webdriver.Chrome()
    # driver.maximize_window()

    # Open the login page
    driver.get("http://bputexam.in/LoginMain.aspx")

    # Wait for the username input field to load
    username_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, "PtuLogin$UserName"))
    )

    # Input login information
    username_input.send_keys(usernameinp)
    password_input = driver.find_element("name", "PtuLogin$Password")
    password_input.send_keys(passwordinp)
    password_input.send_keys(Keys.RETURN)

    # Wait for the link to be clickable
    time.sleep(2)
    hover = ActionChains(driver)
    m = driver.find_element(By.LINK_TEXT, "Student Navigation")
    hover.move_to_element(m).perform()

    # Click on the link
    resultlink = driver.find_element(By.XPATH, '/html/body/form/div[3]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/div/ul/li[4]/div/ul/li[2]/a')
    resultlink.click()

    # wait for page to load
    time.sleep(5)

    try:
        driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lblRollNo"]')
        regno = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lblRollNo"]').text
        name = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lblStudentName"]').text
        branch = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lblBranch"]').text

        table = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_gv1_ctl00"]')

        webtable_df = pd.read_html(table.get_attribute('outerHTML'))[0]

        webtable_df = webtable_df[webtable_df.columns[1:]]

        webtable_df.dropna(how='all', inplace = True)

        new_rows = pd.DataFrame({
            'Sl.No.': regno,
            'Subject Code':name,
            'Subject':branch,
            'Credit': '',
            'Last History': '',
            'Final Grade':''
        }, index=[0])

        webtable_df = pd.concat([new_rows, webtable_df.iloc[:]]).reset_index(drop = True)

        webtable_df.to_csv(f'output/{regno}.csv')
        print(f'{usernameinp} : Done')
    except NoSuchElementException:
        print(f"{usernameinp} : Details doesnot exist")

    # Close the browser window
    driver.quit()


if __name__ == "__main__":
    dfinit = pd.read_csv('source/ece.csv', dtype=str)
    print('ECE')
    for i in range(len(dfinit)):
        usernameinp = dfinit.iloc[i, 0]
        passwordinp = dfinit.iloc[i, 1]
        scrap(usernameinp, passwordinp)