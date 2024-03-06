
# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import time

def create_driver(headless=False):
    options = webdriver.EdgeOptions()
    # level 3 is lowest value for log-level
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    service = Service(EdgeChromiumDriverManager().install())
    import time
    time.sleep(1)
    return webdriver.Edge(options=options, service=service)

def wait(func, *, timeout, interval=0.5):
    """
    func: task to be run and it should have retun values which means success
    timeout: seconds to be wait until the task success
    interval: time between each try.
    """
    start = time.time()
    curr = 0
    retry = 0
    while True:
        curr = time.time() - start
        retry = retry + 1
        res = func()
        if res != None and res != 0:
            return res

        if curr > timeout:
            print(
                f"Timeout! wait_until takes {curr}. timeout={timeout}, interval={interval}, retry={retry}")
            break

        # every 500ms
        time.sleep(interval)

    return res
