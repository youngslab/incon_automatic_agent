# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge

import os
import logging  # Add logging import
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def create_driver( *, headless=False, profile=None):

    options = webdriver.EdgeOptions()
    options.add_argument("window-size=1400,800")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    if profile is not None:
        user_data_path = os.path.join(os.path.expanduser("~"), ".iaa", "edge", profile)
        options.add_argument(f"user-data-dir={user_data_path}")
        
    service = Service(EdgeChromiumDriverManager().install(), log_path=os.devnull)  # Suppress WebDriver logs
    return webdriver.Edge(options=options, service=service)
