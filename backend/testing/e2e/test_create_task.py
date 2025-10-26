import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import requests
# import firebase_utils
# from firebase_utils import get_firestore_client
# from firebase_admin import firestore
# from datetime import datetime


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

    # new task button
    projects_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='new-task']"))
    )
    projects_link.click()

    # enter task details
    # name
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-name']").send_keys("Selenium Testing")
   
    # start & end date
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-start']").send_keys("28/10/2025")
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-end']").send_keys("31/10/2025")

    # priority
    task_prio_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='task-priority']"))
    )
    task_prio_ddl.click()

    task_prio_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='task-priority-option']"))
    )
    task_prio_option.click()
    
    # status
    task_status_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='task-status']"))
    )
    task_status_ddl.click()

    task_status_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='task-status-option']"))
    )
    task_status_option.click()

    # Collaborators
    task_collab_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='task-collab-list']"))
    )
    task_collab_ddl.click()
    
    task_collab_option = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='task-collab-option']"))
    )
    target_name = "Ang Koo Kueh"
    for option in task_collab_option:
        name_element = option.find_element(By.CSS_SELECTOR, ".user-name")
        if target_name.lower() in name_element.text.lower():
            option.click()
            break
    else:
        raise Exception(f"Collaborator '{target_name}' not found in dropdown options.")

    # create task
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-create']").click()

    # validate in success message
    valid_message = 'Task "Selenium Testing" created successfully!'
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".toast-message"), valid_message)
    )

    # ref_dt = datetime.now()
    # ref_ts = ref_dt.timestamp()

    # validate task in homepage
    # tasks = requests.get("http://localhost:8000/tasks").json()
    # assert any(task["task_name"] == "Selenium Testing" for task in tasks)
    
    # validate task in firestore
    # try:
    #     db = get_firestore_client()
    #     tasks_ref = db.collection('Tasks')
    #     task_query = tasks_ref.where('createdAt', '==', ref_ts)
    #     task = task_query.stream()
    #     assert task.to_dict()["task_name"] == "Selenium Testing"

    # except Exception as e:
    #     print(e)
