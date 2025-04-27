# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge

import os
import logging  # Add logging import
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger("Agent")

def create_driver(*, headless=False, profile=None, proxy=None, user_agent=None):

    options = webdriver.EdgeOptions()
    options.add_argument("window-size=1400,800")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("no-sandbox")
    options.add_argument('disable-gpu')

    if headless:
        options.add_argument('headless')
        # headless인 경우 user-agent를 다시 설정. 
        # 실제 non-headless 환경에서 쓰이는 Edge user-agent
        user_agent_ = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        )
        options.add_argument(f'--user-agent={user_agent_}')

    if profile is not None:
        user_data_path = os.path.join(os.path.expanduser("~"), ".iaa", "edge", profile)
        options.add_argument(f"user-data-dir={user_data_path}")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    if user_agent:
        options.add_argument(f'--user-agent={user_agent}')

    service = Service(EdgeChromiumDriverManager().install(), log_path=os.devnull)  # Suppress WebDriver logs
    driver = webdriver.Edge(options=options, service=service)

    # 실제 User-Agent 값 읽기 (브라우저에서 실행)
    try:
        actual_user_agent = driver.execute_script("return navigator.userAgent;")
        logger.info(f"[EdgeDriver] actual user_agent from browser: {actual_user_agent}")
    except Exception as e:
        logger.warning(f"[EdgeDriver] Failed to get userAgent: {e}")

    return  driver
