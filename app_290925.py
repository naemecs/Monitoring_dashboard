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


def get_xpath(driver, element):
    """Generate XPath of a WebElement."""
    return driver.execute_script("""
        function absoluteXPath(element) {
            var comp, comps = [];
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            }

            for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                switch (element.nodeType) {
                    case Node.TEXT_NODE:
                        comp.name = 'text()';
                        break;
                    case Node.ATTRIBUTE_NODE:
                        comp.name = '@' + element.nodeName;
                        break;
                    case Node.ELEMENT_NODE:
                        comp.name = element.nodeName;
                        break;
                }
                comp.position = getPos(element);
            }

            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase();
                if (comp.position !== null && comp.position > 1) {
                    xpath += '[' + comp.position + ']';
                }
            }

            return xpath;
        }
        return absoluteXPath(arguments[0]);
    """, element)


def scrape_tableau_elements():
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

    # Collect all elements with IDs
    elements_with_id = driver.find_elements(By.XPATH, "//*[@id]")

    # Ensure screenshot folder exists
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    all_elements = []
    for idx, el in enumerate(elements_with_id, start=1):
        eid = el.get_attribute("id")
        if eid:
            try:
                etext = el.text.strip()
            except Exception:
                etext = ""
            vis = el.is_displayed()
            tag = el.tag_name
            xpath = get_xpath(driver, el)

            screenshot_path = ""
            if vis:  # Only take screenshot if element is visible
                screenshot_path = os.path.join(screenshot_dir, f"{eid}.png")
                try:
                    el.screenshot(screenshot_path)
                except Exception:
                    screenshot_path = ""

            all_elements.append([eid, etext, "Visible" if vis else "Hidden", tag, xpath, screenshot_path])

    driver.quit()
    return all_elements


def save_to_excel(data, filename="tableau_all_ids.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tableau Elements"

    # Header row
    ws.append(["ID", "Text", "Visibility", "Tag", "XPath", "Screenshot"])

    # Data rows
    for row_idx, row in enumerate(data, start=2):
        ws.append(row[:-1])  # all except screenshot path
        screenshot_path = row[-1]
        if screenshot_path and os.path.exists(screenshot_path):
            img = ExcelImage(screenshot_path)
            img.width, img.height = 200, 120  # resize for readability
            ws.add_image(img, f"F{row_idx}")

    wb.save(filename)
    print(f"\n📊 Data + visible screenshots saved to {filename}")


# Run scraper and save results
elements_data = scrape_tableau_elements()
save_to_excel(elements_data)
print("\n✅ All done!")