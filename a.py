from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import time

# --- Setup Edge driver ---
options = EdgeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Edge(service=EdgeService(), options=options)

# --- Open Tableau dashboard ---
driver.get("https://public.tableau.com/app/profile/rosstest/viz/Telecommunications_2/Dashboard")

# --- Wait until at least one iframe is present ---
WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
)

iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"Found {len(iframes)} iframes in the page.")

all_ids = []

for idx, iframe in enumerate(iframes, start=1):
    try:
        print(f"\n--- Switching to iframe #{idx} ---")
        driver.switch_to.default_content()  # reset before switching
        driver.switch_to.frame(iframe)

        # Wait for any element with an ID inside this iframe
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@id]"))
        )
        time.sleep(3)  # give Tableau some extra time to render

        # Extract all IDs inside this iframe
        elements = driver.find_elements(By.XPATH, "//*[@id]")
        ids = [el.get_attribute("id") for el in elements if el.get_attribute("id")]
        print(f"Iframe #{idx} => Found {len(ids)} IDs")
        
        all_ids.extend(ids)

    except Exception as e:
        print(f"Iframe #{idx} failed: {e}")

# --- Save all IDs to a file ---
with open("tableau_iframe_ids.txt", "w", encoding="utf-8") as f:
    for eid in all_ids:
        f.write(eid + "\n")

print(f"\nTotal collected IDs: {len(all_ids)}")
print("Saved IDs to tableau_iframe_ids.txt")

driver.quit()
