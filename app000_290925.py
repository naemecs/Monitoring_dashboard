import os
import time
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver(browser="edge", headless=False):
    """Launch Selenium driver for Chrome or Edge."""
    if browser == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        return webdriver.Chrome(service=ChromeService(), options=options)

    elif browser == 'edge':
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return webdriver.Edge(service=EdgeService(), options=options)

    else:
        raise Exception(f"Browser '{browser}' not supported.")


def scrape_link_elements():
    driver = get_driver(browser="edge", headless=False)
    driver.get("https://public.tableau.com/app/profile/rosstest/viz/Telecommunications_2/Dashboard")

    # Wait for Tableau iframe
    iframe = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)

    # Wait for Tableau viz content to load
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id]"))
    )
    time.sleep(5)

    # Select only elements that are <a> OR have role="link"
    link_elements = driver.find_elements(By.XPATH, "//*[@id and (self::a or @role='link')]")

    all_links = []
    for idx, el in enumerate(link_elements, start=1):
        eid = el.get_attribute("id")
        if eid:
            etext = el.text.strip() if el.text else ""
            href = el.get_attribute("href")
            vis = el.is_displayed()
            all_links.append([eid, etext, href if href else "", "Visible" if vis else "Hidden"])

    driver.quit()
    return all_links


def save_links_to_excel(data, filename="tableau_link_ids.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Link Data"

    # Header row
    ws.append(["Link ID", "Text", "Href", "Visibility"])

    # Data rows
    for row in data:
        ws.append(row)

    wb.save(filename)
    print(f"\n🔗 Link data saved to {filename}")


# Run scraper and save only link IDs
link_data = scrape_link_elements()
save_links_to_excel(link_data)
print("\n✅ Script completed successfully.")