from camoufox.sync_api import Camoufox
import time

URL = 'https://abrahamjuliot.github.io/creepjs/'

with Camoufox(headless=True) as browser:
    # To Use Virtual Display:
    # pass headless='virtual' above instead of headless=True

    # Open Page
    page = browser.new_page()
    
    # Visit the CreepJS URL
    page.goto(URL)
    
    # Wait for 10 Seconds and Capture Result
    time.sleep(10)
    el = page.locator('#headless-resistance-detection-results>div:first-child')
    el.screenshot(path="pw-camoufox.png")
