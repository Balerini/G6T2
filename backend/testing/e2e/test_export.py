import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    prefs = {"download.default_directory": os.path.abspath("downloads")}
    options.add_experimental_option("prefs", prefs)
    service = Service("C:/WebDrivers/chromedriver.exe")

    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_project_excel_export(driver):
    driver.get("http://localhost:8080/login")

    # --- Login ---
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    driver.find_element(By.ID, "email").send_keys("chow16@gmail.com")
    driver.find_element(By.ID, "password").send_keys("12345")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # load hompage
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "navbar-link"))
    )

    # project link in navbar
    projects_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'navbar-link') and contains(text(), 'Projects')]"))
    )
    projects_link.click()

    # view details for proj yuuuuu
    proj_detail_view_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='view-project-fT2cCbM1GI3GqsBwfpO9']"))
    )
    proj_detail_view_btn.click()

    # export dropdown
    export_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-button']"))
    )
    export_button.click()

    # download as excel 
    download_excel = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-excel']"))
    )
    download_excel.click()

    # wait for download
    time.sleep(5)
    downloaded_files = os.listdir("downloads")

    # validate download folder
    assert any(f.endswith("Project_yuuuu_Tasks_Report.xlsx") for f in downloaded_files), "Excel export file not found"
