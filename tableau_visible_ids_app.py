from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
# For Microsoft Edge.
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from utilities.config_loader import load_config
from dashboard_pages_action.main_monitoring_dasboard import MainMonitoringDashBoard


def get_driver(browser=None, headless=False):
    config = load_config()

    if not browser:
        browser = config['browser']
    browser = browser.lower()

    if headless or bool(config.get('headless')):
        headless = True

    if browser == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_argument("--start-maximized")
        return webdriver.Chrome(service=ChromeService(), options=options)

    elif browser == 'firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        return webdriver.Firefox(service=FirefoxService(), options=options)

    elif browser == 'edge':
        print("browser => ",browser)
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return webdriver.Edge(service=EdgeService(), options=options)

    else:
        raise Exception(f"Browser '{browser}' is not supported.")

driver_obj = get_driver()
driver_obj.get("https://public.tableau.com/app/profile/rosstest/viz/Telecommunications_2/Dashboard")

main_dashboard_page = MainMonitoringDashBoard(driver_obj)

#main_dashboard_page.click_download_button()
# Locate element by its ID
#element = driver_obj.find_element(By.ID, "element_id")
# Replace 'actual_element_id' below with the real ID of the element to find
#element = driver_obj.find_element(By.ID, "actual_element_id")
# --- Wait until Tableau iframe is available ---

# Make sure required imports are present
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

iframe = WebDriverWait(driver_obj, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
)

# --- Switch to iframe ---
driver_obj.switch_to.frame(iframe)

# --- Wait for Tableau viz content to load ---
WebDriverWait(driver_obj, 30).until(
    EC.presence_of_all_elements_located((By.XPATH, "//*[@id]"))
)
time.sleep(5)  # give Tableau time to render fully

# --- Extract IDs inside the iframe ---
#elements_with_id = driver_obj.find_elements(By.XPATH, "//*[@id]")
#ids = [el.get_attribute("id") for el in elements_with_id if el.get_attribute("id")]

#print(f"Found {len(ids)} element IDs inside Tableau iframe:")
##for i, eid in enumerate(ids[:50], start=1):  # show first 50
#    print(f"{i}. {eid}")

# --- Save all IDs to a file ---
#with open("tableau_iframe_ids.txt", "w", encoding="utf-8") as f:
#    for eid in ids:
#        f.write(eid + "\n")
    # --- Extract only visible element IDs ---

elements_with_id = driver_obj.find_elements(By.XPATH, "//*[@id]")
    
visible_ids = [
        el.get_attribute("id") for el in elements_with_id
        if el.get_attribute("id") and el.is_displayed()
    ]
    
print(f"Found {len(visible_ids)} visible element IDs inside Tableau iframe:")
    
for i, eid in enumerate(visible_ids[:50], start=1):  
        # print first 50
        print(f"{i}.{eid}")
    
    # --- Save visible IDs to a file ---
with open("tableau_visible_ids.txt", "w", encoding="utf-8") as f:
        for eid in visible_ids:
            f.write(eid + "\n")

print("Opened the browser..")