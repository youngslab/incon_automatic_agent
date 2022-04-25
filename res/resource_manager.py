
import os

class resource_manager:

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))

    def get(self, img:str):
        directory = img.split('_', 1)[0]
        filepath = os.path.join(self.path, directory, img)
        if not os.path.isfile(filepath):
            return None
        return filepath

        