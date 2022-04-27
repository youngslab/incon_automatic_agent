
import os, json


def __account_load_json(filepath):
    with open(filepath, 'r')  as f:
        return json.loads(f.read())

def __account_filepath():
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, ".accounts.json")
    
__account_data = None

def __account_init():
    global __account_data
    filepath = __account_filepath()
    __account_data = __account_load_json(filepath)

def account_get(organization:str, key:str) -> str:
        global __account_data
        if __account_data == None:
            __account_init()
        return __account_data[organization][key]


class resource_manager:

    def get(img:str):
        basedir = os.path.dirname(os.path.abspath(__file__))
        directory = img.split('_', 1)[0]
        filepath = os.path.join(basedir, directory, img)
        if not os.path.isfile(filepath):
            return None
        return filepath    
    
    @classmethod
    def get_account(cls, organization:str, key:str) -> str:
        return account_get(organization, key)