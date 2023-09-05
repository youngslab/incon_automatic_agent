
from .browser import *

import os
if os.name == "nt":
    from .win32 import *


__version__ = "0.0.1"

# We need an explicit __all__ because the above won't otherwise be exported.
__all__ = [

]
