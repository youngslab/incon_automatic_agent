

import os
import json
import logging


def logger():
    return logging.getLogger(__package__)


def __account_load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


def __account_filepath():
    path = os.path.join(os.path.expanduser('~'), ".iaa")
    return os.path.join(path, "account.json")

__account_data = None

def __init_account():
    global __account_data
    if __account_data == None:
        filepath = __account_filepath()
        if not os.path.exists(filepath):
            raise Exception(
                f"Failed to find the account file. filepath={filepath}")
        __account_data = __account_load_json(filepath)




def account_get(org: str, key: str) -> str:
    __init_account()

    if not __account_data.get(org):
        raise Exception(f"Failed to find the organization. org={org}")
        return None

    if not __account_data[org].get(key):
        raise Exception(f"Failed to find the key. org={org}, key={key}")
        return None

    return __account_data[org][key]


def account_get_raw_data():
    __init_account()
    return __account_data
