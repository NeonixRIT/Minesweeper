import numpy as np

from itertools import permutations

import difficulties
from difficulties import Difficulties
from difficulty import Difficulty
from location import Location
from tile import Tile

class Board:
    def __init__(self, difficulty: Difficulties):
        self.difficulty = difficulty.value
        self.board = [[Tile(x, y, False) for x in range(self.difficulty.width)] for y in range(self.difficulty.height)]

    def __str__(self) -> str:
        result = ''
        for i, row in enumerate(self.board):
            for tile in row:
                result += str(tile)
            result += '\n' if i + 1 < len(self.board) else ''
        return result

    def populate(self, start_space: Location):
        diffs = {(0, 1), (0, -1),
                 (1, 0), (1, 1), (1, -1),
                 (-1, 0), (-1, 1), (-1, -1)}

        blank_spaces = [start_space]
        iter_blank_spaces = [start_space]
        for _ in range(np.random.randint(0, (self.difficulty.height * self.difficulty.width) // 3 + 5)):
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
            x = np.random.randint(0, self.difficulty.height)
            y = np.random.randint(0, self.difficulty.height)
            loc = Location(x, y)
            if loc in blank_spaces:
                continue
            bombs.add(loc)
        self.board = [[Tile(x, y, Location(x, y) in bombs) for x in range(self.difficulty.width)] for y in range(self.difficulty.height)]
        self.__populate_hints()

    def __populate_hints(self):
        diffs = {(0, 1), (0, -1),
                 (1, 0), (1, 1), (1, -1),
                 (-1, 0), (-1, 1), (-1, -1)}
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                if tile.is_bomb:
                    continue
                for loc in (tile.coords + diff for diff in diffs):
                    if loc.y >= self.difficulty.height or loc.x >= self.difficulty.width:
                        continue
                    if loc.y < 0 or loc.x < 0:
                        continue
                    neighbor = self.board[loc.y][loc.x]
                    tile.neighbors.add(neighbor)
                    if neighbor.is_bomb:
                        tile.hint += 1


def main():
    b = Board(Difficulties.EASY)
    b.populate(Location(3, 3))
    b.board[3][3].flip()
    print(b)


if __name__ == '__main__':
    main()