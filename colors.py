from enum import Enum

class Colors(Enum):
    WHITE = '\033[0m' # reset or not flipped
    RED = '\033[1;31m' # bomb
    GREEN = '\033[1;32m' # 1
    CYAN = '\033[0;36m' # 2
    BLUE = '\033[1;34m' # 3
    PURPLE = '\033[1;35m' # 4
    YELLOW = '\033[0;33m' # 5+