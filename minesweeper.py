import numpy as np

from board import Board
from difficulty import Difficulty
from difficulties import Difficulties
from location import Location
from status import Status
from utils import clear


class Minesweeper:
    def __init__(self, difficulty: Difficulties):
        self.difficulty = difficulty
        self.board = Board(difficulty)
        self.moves = 0
        self.status = Status.IN_PROGRESS
        self.tiles_remaining = difficulty.value.height * difficulty.value.width

    def __str__(self) -> str:
        return f'Moves: {self.moves}\nDifficulty: {self.difficulty.value}\nTiles: {self.tiles_remaining}\n{self.board}'

    def in_bounds(self, location: Location) -> bool:
        return (location.y >= 0 and location.x >= 0) and (location.y < self.board.difficulty.height and location.x < self.board.difficulty.width)

    def make_move(self, x: int, y: int):
        if self.status == Status.WIN or self.status == Status.LOSS:
            return
        if self.board.tiles[y][x].is_flipped:
            return
        if self.moves == 0:
            self.board.populate(Location(x, y))
        self.board.tiles[y][x].flip()
        self.moves += 1
        self.tiles_remaining = len([tile for tile in np.array(self.board.tiles).flatten() if not tile.is_flipped and not tile.is_bomb])
        if self.board.tiles[y][x].is_bomb:
            self.status = Status.LOSS
        elif not self.tiles_remaining and not [tile for tile in np.array(self.board.tiles).flatten() if tile.is_flipped and tile.is_bomb]:
            self.status = Status.WIN

    def play(self):
        while True:
            clear()
            print(self)
            move = input("Enter a coordinate x and y values separated by a space: ").split()
            x = int(move[0])
            y = int(move[1])
            self.make_move(x, y)


def main():
    game = Minesweeper(difficulty=Difficulties.EASY)
    game.play()


if __name__ == '__main__':
    main()

# TODO: ?
# refactor solving to functions

# 50:50 interaction when not a corner and tile up/down/left/right of bomb is blank
# with equal (hints active on that square)/2
