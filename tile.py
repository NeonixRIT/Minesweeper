from colors import Colors
from location import Location


COLORS = {1: Colors.GREEN.value,
          2: Colors.CYAN.value,
          3: Colors.BLUE.value,
          4: Colors.PURPLE.value,
          5: Colors.YELLOW.value}


class Tile:
    def __init__(self, x: int, y: int, bomb: bool = False, hint: int = 0, is_flipped: bool = False):
        self.coords = Location(x, y)
        self.is_bomb = bomb
        self.is_flipped = is_flipped
        self.hint = hint
        self.neighbors = set()

    def __str__(self) -> str:
        if self.is_flipped:
            color_hint = self.hint * -1 if self.hint < 0 else self.hint
            if 0 < self.hint < 1:
                color_hint = 1
            if 1 < self.hint < 2:
                color_hint = 2
            if 2 < self.hint < 3:
                color_hint = 3
            if 3 < self.hint < 4:
                color_hint = 4
            if 4 < self.hint < 5:
                color_hint = 5
            if 5 < self.hint:
                color_hint = 5

            val = round(self.hint + 0.5) if isinstance(self.hint, float) else self.hint
            return f'{Colors.RED.value}[●]{Colors.WHITE.value}' if self.is_bomb else '[ ]' if self.hint <= 0 else f'{COLORS[color_hint]}[{val}]{Colors.WHITE.value}'
        return '[X]'

    def __repr__(self) -> repr:
        return f'Tile(coords={self.coords}, is_bomb={self.is_bomb}, is_flipped={self.is_flipped}, hint={self.hint}, neighbors=[...])'

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.coords == other.coords

    def __hash__(self):
        return hash(str(self.coords) + 'unique string... lol')

    def flip(self):
        self.is_flipped = not self.is_flipped
        if self.hint == 0 and not self.is_bomb:
            for neighbor in self.neighbors:
                if not neighbor.is_flipped:
                    neighbor.flip()
