from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Setup Edge options ---
edge_options = Options()
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--disable-blink-features=AutomationControlled")

# --- Start Edge WebDriver ---
service = Service("msedgedriver")  # replace with full path if needed
driver = webdriver.Edge(service=service, options=edge_options)

try:
    url = "https://public.tableau.com/app/profile/rosstest/viz/Telecommunications_2/Dashboard"
    driver.get(url)

    # --- Wait until Tableau iframe is available ---
    iframe = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )

    # --- Switch into Tableau iframe ---
    driver.switch_to.frame(iframe)

    # --- Wait until elements with IDs exist ---
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id]"))
    )
    time.sleep(5)  # give Tableau time to render fully

    # --- Extract only visible element IDs ---
    elements_with_id = driver.find_elements(By.XPATH, "//*[@id]")
    visible_ids = [
        el.get_attribute("id") for el in elements_with_id
        if el.get_attribute("id") and el.is_displayed()
    ]

    print(f"Found {len(visible_ids)} visible element IDs inside Tableau iframe:")
    for i, eid in enumerate(visible_ids[:50], start=1):  # print first 50
        print(f"{i}. {eid}")

    # --- Save visible IDs to a file ---
    with open("tableau_visible_ids.txt", "w", encoding="utf-8") as f:
        for eid in visible_ids:
            f.write(eid + "\n")

finally:
    driver.quit()
