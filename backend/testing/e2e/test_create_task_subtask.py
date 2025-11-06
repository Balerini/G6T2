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

    # new task button
    new_task = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='new-task']"))
    )
    new_task.click()

    # enter task details
    # name
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-name']").send_keys("Selenium Testing")
   
    # start & end date
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-start']").send_keys("28/11/2025")
    driver.find_element(By.CSS_SELECTOR, "[data-testid='task-end']").send_keys("30/11/2025")

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
    
    task_collab_options = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='task-collab-option']"))
    )
    target_name = "Ang Koo Kueh"
    for option in task_collab_options:
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

    # add subtask now
    # project link in navbar
    projects_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-projects']"))
    )
    projects_link.click()

    # click standalone tasks
    standalone_tasks = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='standalone-task']"))
    )
    standalone_tasks.click()

    # click view task details for "Selenium Testing"
    task_list = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='task-card']"))
    )
    target_task = "Selenium Testing"
    for task in task_list:
        name_element = task.find_element(By.CSS_SELECTOR, ".task-title")
        if target_task.lower() in name_element.text.lower():
            task.find_element(By.CSS_SELECTOR, "[data-testid='task-view-details']").click()
            break
    else:
        raise Exception(f"Task '{target_task}' not found in page.")
    
    time.sleep(2)

    # add subtask
    driver.find_element(By.CSS_SELECTOR, "[data-testid='add-subtask']").click()

    # fields
    # name
    time.sleep(5) 
    driver.find_element(By.CSS_SELECTOR, "[data-testid='subtask-name']").send_keys("Selenium Sub Testing")
   
    # start & end date
    driver.find_element(By.CSS_SELECTOR, "[data-testid='subtask-start']").send_keys("29")
    driver.find_element(By.CSS_SELECTOR, "[data-testid='subtask-end']").send_keys("30")

    # priority
    subtask_prio_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='subtask-priority']"))
    )
    subtask_prio_ddl.click()

    subtask_prio_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='subtask-priority-option']"))
    )
    subtask_prio_option.click()
    
    # status
    subtask_status_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='subtask-status']"))
    )
    subtask_status_ddl.click()

    subtask_status_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='subtask-status-option']"))
    )
    subtask_status_option.click()

    # Collaborators
    subtask_collab_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='subtask-collab-list']"))
    )
    subtask_collab_ddl.click()
    
    subtask_collab_options = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='subtask-collab-option']"))
    )
    target_name = "Ang Koo Kueh"
    for option in subtask_collab_options:
        name_element = option.find_element(By.CSS_SELECTOR, ".user-name")
        if target_name.lower() in name_element.text.lower():
            option.click()
            break
    else:
        raise Exception(f"Collaborator '{target_name}' not found in dropdown options.")

    # create subtask
    driver.find_element(By.CSS_SELECTOR, "[data-testid='subtask-create']").click()

    time.sleep(2)

    # validate in success message
    valid_message = '✅ Subtask created successfully!'
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "[data-testid='subtask-toast']"), valid_message)
    )