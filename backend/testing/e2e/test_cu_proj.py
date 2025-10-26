import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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

    # new proj
    new_proj = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='new-proj']"))
    )
    new_proj.click()

    # name
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-name']").send_keys("Selenium Project Testing")

    # start & end date
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-start']").send_keys("27/11/2025")
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-end']").send_keys("01/12/2025")

    # Collaborators
    proj_collab_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='proj-collab-list']"))
    )
    proj_collab_ddl.click()
    
    proj_collab_options = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='proj-collab-option']"))
    )
    target_name = "Ang Koo Kueh"
    for option in proj_collab_options:
        name_element = option.find_element(By.CSS_SELECTOR, ".user-name")
        if target_name.lower() in name_element.text.lower():
            option.click()
            break
    else:
        raise Exception(f"Collaborator '{target_name}' not found in dropdown options.")

    # close collab ddl
    proj_collab_ddl = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='proj-collab-list']"))
    )
    proj_collab_ddl.click()

    # create proj
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-create']").click()

    time.sleep(2)

    # validate in success message
    valid_message = '✅ Project "Selenium Project Testing" created successfully!'
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "[data-testid='proj-toast']"), valid_message)
    )

    # update proj
    # project link in navbar
    projects_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-projects']"))
    )
    projects_link.click()

    # view details for proj Selenium Project Testing
    proj_list = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='proj-list']"))
    )
    target_proj = "Selenium Project Testing"
    for proj_card in proj_list:
        name_element = proj_card.find_element(By.CSS_SELECTOR, ".project-title")
        if target_proj.lower() in name_element.text.lower():
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", proj_card)

            # Wait for the button inside that card
            view_btn = WebDriverWait(proj_card, 5).until(
                lambda c: c.find_element(By.CSS_SELECTOR, "[data-testid='proj-details']")
            )

            # Scroll again if button still not in view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_btn)

            # Click via JavaScript to avoid overlay/intercept issues
            driver.execute_script("arguments[0].click();", view_btn)
            # print(f"✅ Clicked 'View Project Details' for '{target_proj}'")
            found = True
            break
    else:
        raise Exception(f"Collaborator '{target_proj}' not found in page.")
    
    # click edit
    driver.find_element("tag name", "body").send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)

    project_edit = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='proj-edit']"))
    )
    project_edit.click()

    # desc
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-desc']").send_keys("Please god, let this work.")

    # update changes
    driver.find_element(By.CSS_SELECTOR, "[data-testid='proj-create']").click()
    
    # validate in success message
    valid_message = 'Project updated successfully!'
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "[data-testid='proj-details-notif']"), valid_message)
    )







