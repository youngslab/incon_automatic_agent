
import os, json

class resource_manager:

    def get(img:str):
        basedir = os.path.dirname(os.path.abspath(__file__))
        directory = img.split('_', 1)[0]
        filepath = os.path.join(basedir, directory, img)
        if not os.path.isfile(filepath):
            return None
        return filepath    
    
