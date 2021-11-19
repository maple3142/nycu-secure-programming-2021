#!/usr/bin/env python3
import time
import os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

TIMEOUT = 5
BASE_URL = "https://profile.chal.h4ck3r.quest"


def browse(reported_url):
    options = Options()
    # options.headless = True
    # options.add_argument('--headless')
    options.add_argument("--no-sandbox")  # https://stackoverflow.com/a/45846909
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # https://stackoverflow.com/a/50642913
    options.add_argument("--disable-gpu")
    chrome = Chrome(options=options)
    # https://stackoverflow.com/a/47695227
    chrome.set_page_load_timeout(TIMEOUT)
    chrome.set_script_timeout(TIMEOUT)

    # login
    print("[Login...]")
    chrome.get(BASE_URL + "/login")
    chrome.find_element_by_name("username").send_keys("testing11")
    chrome.find_element_by_name("password").send_keys("testing11")
    chrome.find_element_by_tag_name("button").click()

    print("[Visiting...]")
    # visit
    chrome.get(reported_url)

    time.sleep(300)
    chrome.get(BASE_URL + "/reset")
    chrome.quit()
    print("[DONE]")
    return


browse("https://49dc-140-115-216-194.ngrok.io/open.html")
