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
            color_hint = 5 if self.hint > 5 else self.hint
            return f'{Colors.RED.value}[●]{Colors.WHITE.value}' if self.is_bomb else f'{COLORS[color_hint]}[{self.hint}]{Colors.WHITE.value}' if self.hint > 0 else '[ ]'
        return '[X]'

    def __repr__(self) -> repr:
        return f'Tile(coords={self.coords}, is_bomb={self.is_bomb}, is_flipped={self.is_flipped}, hint={self.hint}, neighbors=[...])'

    def flip(self):
        self.is_flipped = not self.is_flipped
        if self.hint == 0 and not self.is_bomb:
            for neighbor in self.neighbors:
                if not neighbor.is_flipped:
                    neighbor.flip()
