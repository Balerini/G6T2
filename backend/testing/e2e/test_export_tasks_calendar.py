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
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-projects']"))
    )
    projects_link.click()

    # view details for proj yuuuuu
    proj_list = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='proj-list']"))
    )
    target_name = "yuuuu"
    for proj_card in proj_list:
        name_element = proj_card.find_element(By.CSS_SELECTOR, ".project-title")
        if target_name.lower() in name_element.text.lower():
            time.sleep(1)
            proj_card.find_element(By.CSS_SELECTOR, "[data-testid='proj-details']").click()
            break
    else:
        raise Exception(f"Collaborator '{target_name}' not found in dropdown options.")

    # export task dropdown
    export_task_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-task-button']"))
    )
    export_task_button.click()

    # download as pdf 
    download_task_pdf = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-task-pdf']"))
    )
    download_task_pdf.click()

    # wait for download
    time.sleep(5)
    downloaded_files = os.listdir("downloads")

    # validate download folder
    assert any(f.endswith("Project_yuuuu_Tasks_Report.pdf") for f in downloaded_files), "PDF export file not found"


    # export task dropdown
    export_task_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-task-button']"))
    )
    export_task_button.click()

    # download as excel 
    download_task_excel = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-task-excel']"))
    )
    download_task_excel.click()

    # wait for download
    time.sleep(5)
    downloaded_files = os.listdir("downloads")

    # validate download folder
    assert any(f.endswith("Project_yuuuu_Tasks_Report.xlsx") for f in downloaded_files), "Excel export file not found"




    # export calendar dropdown      
    team_schedule = driver.find_element(By.CSS_SELECTOR, ".team-schedule-container")
    driver.execute_script("arguments[0].scrollIntoView(true);", team_schedule)
    time.sleep(1)
    
    export_calendar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-calendar-button']"))
    )
    export_calendar_button.click()

    # download as pdf 
    download_calendar_pdf = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-calendar-pdf']"))
    )
    download_calendar_pdf.click()

    # wait for download
    time.sleep(5)
    downloaded_files = os.listdir("downloads")

    # validate download folder
    assert any(f.endswith("yuuuu_Team_Calendar.pdf") for f in downloaded_files), "PDF export file not found"


    # export calendar dropdown
    export_calendar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-calendar-button']"))
    )
    export_calendar_button.click()

    # download as excel 
    download_calendar_excel = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='export-calendar-excel']"))
    )
    download_calendar_excel.click()

    # wait for download
    time.sleep(5)
    downloaded_files = os.listdir("downloads")

    # validate download folder
    assert any(f.endswith("yuuuu_Team_Calendar.xlsx") for f in downloaded_files), "Excel export file not found"
