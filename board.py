import numpy as np

import difficulties
from difficulties import Difficulties
from difficulty import Difficulty
from location import Location
from tile import Tile


class Board:
    def __init__(self, difficulty: Difficulties):
        self.difficulty = difficulty.value
        self.tiles = [[Tile(x, y, False) for x in range(self.difficulty.width)] for y in range(self.difficulty.height)]

    def __str__(self) -> str:
        result = ''
        for i, row in enumerate(self.tiles):
            for tile in row:
                result += str(tile)
            result += '\n' if i + 1 < len(self.tiles) else ''
        return result

    def flip_all_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.is_flipped = True

    def reveal_bombs(self):
        for row in self.tiles:
            for tile in row:
                tile.is_flipped = tile.is_bomb or tile.is_flipped

    def copy(self):
        diff = Difficulty(self.difficulty.height, self.difficulty.width, self.difficulty.bombs)
        if diff == Difficulties.EASY.value:
            diff = Difficulties.EASY
        if diff == Difficulties.MEDIUM.value:
            diff = Difficulties.MEDIUM
        if diff == Difficulties.HARD.value:
            diff = Difficulties.HARD
        new_board = Board(difficulty=diff)
        new_board.tiles = [[Tile(tile.coords.x, tile.coords.y, False, tile.hint if tile.is_flipped else 0, tile.is_flipped) for tile in row] for row in self.tiles]
        for y, row in enumerate(new_board.tiles):
            for x, tile in enumerate(row):
                tile.neighbors = [new_board.tiles[neighbor.coords.y][neighbor.coords.x] for neighbor in self.tiles[y][x].neighbors]
        return new_board

    def populate(self, start_space: Location):
        diffs = {(0, 1), (0, -1),
                 (1, 0), (1, 1), (1, -1),
                 (-1, 0), (-1, 1), (-1, -1)}

        blank_spaces = [start_space]
        iter_blank_spaces = [start_space]
        for _ in range(np.random.randint(5, (self.difficulty.height * self.difficulty.width) // 4)):
            space = iter_blank_spaces[-1]
            for loc in [space + diff for diff in diffs]:
                is_blank = np.random.randint(0, 20) == 3
                if is_blank:
                    iter_blank_spaces.append(loc)
            if iter_blank_spaces:
                blank_spaces = blank_spaces + iter_blank_spaces
                iter_blank_spaces = [iter_blank_spaces[-1]]
        blank_spaces = set(blank_spaces + [space + diff for diff in diffs for space in blank_spaces])

        bombs = set()
        while len(bombs) < self.difficulty.bombs:
            x = np.random.randint(0, self.difficulty.width)
            y = np.random.randint(0, self.difficulty.height)
            loc = Location(x, y)
            if loc in blank_spaces:
                continue
            bombs.add(loc)
        self.tiles = [[Tile(x, y, Location(x, y) in bombs) for x in range(self.difficulty.width)] for y in range(self.difficulty.height)]
        self.__populate_hints()

    def __populate_hints(self):
        diffs = {(0, 1), (0, -1),
                 (1, 0), (1, 1), (1, -1),
                 (-1, 0), (-1, 1), (-1, -1)}
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                for loc in (tile.coords + diff for diff in diffs):
                    if loc.y >= self.difficulty.height or loc.x >= self.difficulty.width:
                        continue
                    if loc.y < 0 or loc.x < 0:
                        continue
                    neighbor = self.tiles[loc.y][loc.x]
                    tile.neighbors.add(neighbor)
                    if neighbor.is_bomb and not tile.is_bomb:
                        tile.hint += 1


def main():
    b = Board(Difficulties.EASY)
    b.populate(Location(3, 3))
    b.tiles[3][3].flip()
    print(b)


if __name__ == '__main__':
    main()
