from board import Board
from difficulty import Difficulty
from difficulties import Difficulties
from location import Location
from tile import Tile

class Minesweeper:
    def __init__(self, difficulty: Difficulties):
        self.difficulty = difficulty
        self.board = Board(difficulty)
        self.moves = 0

    def __str__(self) -> str:
        return f'Moves: {self.moves}\nDifficulty: {self.difficulty.value}\n{self.board}'

    def play(self):
        while True:
            clear()
            print(self)
            move = input("Enter a coordinate x and y values separated by a space: ").split()
            x = int(move[0])
            y = int(move[1])
            self.make_move(x, y)

    def make_move(self, x: int, y: int):
        if self.board.board[y][x].is_flipped:
            return
        if self.moves == 0:
            self.board.populate(Location(x, y))
        self.board.board[y][x].flip()
        self.moves += 1


def clear():
    print("\033c\033[3J\033[2J\033[0m\033[H")


def weights_board(minesweeper: Minesweeper) -> Board:
    diffs = {(0, 1), (0, -1),
             (1, 0), (1, 1), (1, -1),
             (-1, 0), (-1, 1), (-1, -1)}

    weights = {}
    for y, row in enumerate(minesweeper.board.board):
        for x, tile in enumerate(row):
            weights[tile.coords] = 0

    for y, row in enumerate(minesweeper.board.board):
        for x, tile in enumerate(row):
            if not tile.is_flipped:
                continue
            for loc in [tile.coords + diff for diff in diffs]:
                if loc.y >= minesweeper.difficulty.value.height or loc.x >= minesweeper.difficulty.value.width:
                    continue
                if loc.y < 0 or loc.x < 0:
                    continue
                if minesweeper.board.board[loc.y][loc.x].is_flipped:
                    continue
                weights[loc] += 1

    weight_b = Board(minesweeper.difficulty)
    weight_b.board = [[Tile(x, y, False, weights[Location(x, y)]) for x in range(minesweeper.difficulty.value.width)] for y in range(minesweeper.difficulty.value.height)]
    for y, row in enumerate(weight_b.board):
        for x, tile in enumerate(row):
            tile.is_flipped = True
    return weight_b


game = Minesweeper(Difficulties.EASY)
game.make_move(3, 3)
print(game)
print()
b = weights_board(game)
print(b)

for row in game.board.board:
    for tile in row:
        tile.is_flipped = True

print(game)

# TODO: ?
# Highest hint in a 'cluster' seems to be a bomb (maybe w/ 2 iterations?)

# identify corners to be bombs

# Identify highest hints in a cluster and recalculate weights with
# identified bomb and tiles adjacent to those bombs having - 1 hint

