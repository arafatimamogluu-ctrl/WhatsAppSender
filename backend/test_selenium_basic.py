from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_basic():
    print("Initializing Chrome Driver...")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("Driver initialized.")
        
        print("Navigating to google.com...")
        driver.get("https://www.google.com")
        print("Page title:", driver.title)
        
        time.sleep(2)
        driver.quit()
        print("Test passed.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_basic()
