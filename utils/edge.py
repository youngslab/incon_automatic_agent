# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def create_driver(headless=False):
    options = webdriver.EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(options=options, service=service)
