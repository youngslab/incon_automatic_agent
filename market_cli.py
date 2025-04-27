from datetime import datetime
import sys
import os
import traceback
from dotenv import load_dotenv

from utils.logger import setup_agent_logger

# fmt: off
load_dotenv()
pythonpath = os.getenv("PYTHONPATH")
if pythonpath:
    absolute_paths = [os.path.abspath(path) for path in pythonpath.split(os.pathsep)]
    sys.path.extend(absolute_paths)

import org
from org.markets import MarketFactory
from utils.edge import create_driver
import org.d2b
import org.kepco
import org.g2b
import automatic.automatic

def print_help():
    print("\n사용 가능한 명령:")
    print("  login <market>                : 마켓 생성 및 로그인")
    print("  register <code>               : 코드로 register 실행")
    print("  participate <code> <price>    : 코드와 가격으로 participate 실행")
    print("  help                          : 명령어 도움말")
    print("  exit                          : 종료 (Ctrl+C로도 종료 가능)\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Market CLI")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    args, unknown = parser.parse_known_args()

    if args.debug:
        loggers = [org.g2b.LOGGER_G2B, 
               org.d2b.LOGGER_D2B,
               org.kepco.LOGGER_KEPCO, 
               automatic.automatic.LOGGER_AUTOMATIC]
        log_path = os.path.join('~', '.iaa', 'log', f"incon_agent_cli.log")
        log_path = os.path.expanduser(log_path)
        setup_agent_logger(loggers, log_path)

    drv = create_driver(headless=False, profile="market")
    market = None
    print("CLI 모드 시작. 'help' 입력 시 명령어 안내를 볼 수 있습니다.")
    print_help()
    try:
        while True:
            try:
                cmd = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n종료합니다.")
                break

            if not cmd:
                continue

            args_line = cmd.split()
            if args_line[0] == "help":
                print_help()
            elif args_line[0] == "exit":
                print("종료합니다.")
                break
            elif args_line[0] == "login":
                if len(args_line) < 2:
                    print("사용법: login <market>")
                    continue
                market_name = args_line[1]
                print(f"MarketFactory로 마켓 객체를 생성합니다...")
                market = MarketFactory.create(drv, market_name)
                if market is None:
                    print(f"지원하지 않는 마켓명입니다: {market_name}")
                else:
                    print(f"마켓 객체가 성공적으로 생성되었습니다: {market.name}")
                    try:
                        market.login()
                        print("로그인 성공")
                    except Exception as e:
                        print(f"로그인 중 오류 발생: {e}")
                        traceback.print_exc()
            elif args_line[0] == "register":
                if market is None:
                    print("먼저 login <market> 명령으로 마켓에 로그인하세요.")
                    continue
                if len(args_line) < 2:
                    print("사용법: register <code>")
                    continue
                code = args_line[1]
                try:
                    result = market.register(code)
                    print(f"register 결과: {result}")
                except Exception as e:
                    print(f"register 중 오류 발생: {e}")
                    traceback.print_exc()
            elif args_line[0] == "participate":
                if market is None:
                    print("먼저 login <market> 명령으로 마켓에 로그인하세요.")
                    continue
                if len(args_line) < 3:
                    print("사용법: participate <code> <price>")
                    continue
                code = args_line[1]
                price = args_line[2]
                try:
                    result = market.participate(code, price)
                    print(f"participate 결과: {result}")
                except Exception as e:
                    print(f"participate 중 오류 발생: {e}")
                    traceback.print_exc()
            elif args_line[0] == "capture":
                # Windows 및 Unix 모두에서 안전하게 경로 처리
                home_dir = os.path.expanduser("~")
                screenshot_dir = os.path.join(home_dir, ".iaa", "cli")
                screenshot_path = os.path.join(screenshot_dir, "capture.png")
                os.makedirs(screenshot_dir, exist_ok=True)
                try:
                    drv.save_screenshot(screenshot_path)
                    print(f"스크린샷이 저장되었습니다: {screenshot_path}")
                except Exception as e:
                    print(f"스크린샷 저장 중 오류 발생: {e}")
                    traceback.print_exc()
            else:
                print("알 수 없는 명령입니다. 'help'를 입력해보세요.")
    finally:
        if drv is not None:
            print("드라이버 종료")
            drv.quit()

if __name__ == "__main__":
    main()
