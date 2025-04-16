import glob
import logging
import os
import json
from datetime import datetime, timedelta
import logging

# StreamHandler 설정 함수
def setup_stream_handler(formatter, level, loggers):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    for name in loggers:
        logger = logging.getLogger(name)
        logger.addHandler(console_handler)


# FileHandler 설정 함수
def setup_file_handler(formatter, level, file_path, loggers):
    """
    FileHandler 설정
    :param formatter: 로그 메시지 포매터
    :param level: 로그 레벨
    :param file_path: 로그 파일 경로
    :param loggers: 설정할 로거 이름 리스트
    """
    file_path = os.path.expanduser(file_path)  # ~ 경로 처리
    file_directory = os.path.dirname(file_path)

    # 디렉토리가 없으면 생성
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    file_handler = logging.FileHandler(file_path, mode="w", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    for name in loggers:
        logger = logging.getLogger(name)
        logger.addHandler(file_handler)


def flush_file_handler(loggers):
    """모든 FileHandler를 flush."""
    for name in loggers:
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

# 오래된 로그 파일 삭제 함수
def delete_old_loggers(log_directory, extension="*.log", days=10):
    """
    지정된 디렉토리에서 오래된 로그 파일 삭제.
    :param log_directory: 로그 파일이 저장된 디렉토리
    :param extension: 삭제할 파일 확장자 (기본값: *.log)
    :param days: 기준 일수 (기본값: 10일)
    """
    log_directory = os.path.expanduser(log_directory)  # ~ 경로 처리
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)  # 디렉토리가 없으면 생성
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    old_files = glob.glob(os.path.join(log_directory, extension))
    
    for file in old_files:
        try:
            # 파일의 수정 날짜를 확인
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file))
            if file_mtime < cutoff_date:
                os.remove(file)
                print(f"Deleted old log file: {file}")
        except OSError as e:
            print(f"Error deleting file {file}: {e}")

# 에이전트 로거 설정 함수
def setup_agent_logger(loggers, log_path):
    """
    에이전트 로거 설정: 기존 로그 삭제 후 StreamHandler와 FileHandler 등록.
    :param loggers: 설정할 로거 이름 리스트
    :param log_directory: 로그 파일 저장 디렉토리
    """
    #  Setup default log level
    for name in loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

    log_path = os.path.expanduser(log_path)  # ~ 경로 처리
    log_directory = os.path.dirname(log_path)

    # 이전 로그 파일 삭제
    delete_old_loggers(log_directory=log_directory)

    # Formatter 생성
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # StreamHandler 설정
    setup_stream_handler(formatter, logging.INFO, loggers)

    # FileHandler 설정 (파일 경로에 날짜 추가)    
    setup_file_handler(formatter, logging.DEBUG, log_path, loggers)


def logger_update_handler_filename_if_neccessary(config: dict, handler_name: str, filename: str) -> bool:
    if not 'handlers' in config.keys():
        return False

    handlers = config['handlers']
    if not handler_name in handlers.keys():
        return False

    handler = handlers[handler_name]
    if 'filename' in handler.keys():
        return False

    handler['filename'] = filename
    return True


def iaa_load_logger_config(filepath):
    if not os.path.exists(filepath):
        return None

    print("open logger.json")
    with open(filepath, 'r') as f:
        config = json.load(f)
        return config


def logger_create_log_filepath(basedir):
    filename = f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    dir = os.path.join(basedir, "log")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return os.path.join(dir, filename)
