
import os
import time
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:5000"
)

SELENIUM_URL = os.getenv(
    "SELENIUM_URL",
    "http://localhost:4444/wd/hub"
)


def test_application_health():
    """TC01: Check application health."""

    url = BASE_URL + "/healthz"

    for attempt in range(30):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                assert response.status == 200
                return
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)


@pytest.fixture
def browser():
    """Start Chrome through Selenium Grid."""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None

    for attempt in range(30):
        try:
            driver = webdriver.Remote(
                command_executor=SELENIUM_URL,
                options=options
            )
            break
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)

    yield driver

    if driver:
        driver.quit()


def test_homepage_loads(browser):
    """TC02: Verify homepage loads."""

    browser.get(BASE_URL)

    assert browser.current_url.startswith(BASE_URL)


def test_page_title(browser):
    """TC03: Verify browser page title."""

    browser.get(BASE_URL)

    assert browser.title is not None


def test_page_content(browser):
    """TC04: Verify page body is displayed."""

    browser.get(BASE_URL)

    body = browser.find_element(By.TAG_NAME, "body")

    assert body.is_displayed()
