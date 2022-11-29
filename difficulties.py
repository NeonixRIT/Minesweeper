from enum import Enum

from difficulty import Difficulty

class Difficulties(Enum):
    EASY = Difficulty(height=9, width=9, bombs=10)
    MEDIUM = Difficulty(height=16, width=16, bombs=40)
    HARD = Difficulty(height=16, width=30, bombs=99)
