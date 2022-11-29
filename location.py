from collections.abc import Iterable

class Location:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __add__(self, other):
        if isinstance(other, Location):
            x = self.x + other.x
            y = self.y + other.y
            return Location(x, y)
        elif isinstance(other, Iterable) and len(other) == 2:
            x = self.x + other[0]
            y = self.y + other[1]
            return Location(x, y)
        raise NotImplemeneted("")

    def __sub__(self, other):
        if isinstance(other, Location):
            distance = (((other.x - self.x) ** 2) + ((other.y - self.y) ** 2)) ** 0.5
            return distance
        elif isinstance(other, Iterable) and len(other) == 2:
            distance = (((other[0] - self.x) ** 2) + ((other[1] - self.y) ** 2)) ** 0.5
            return distance
        raise NotImplemeneted("")

    def __hash__(self):
        return hash(f'({self.x}, {self.y})')

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.x == other.x and self.y == other.y
        return False
