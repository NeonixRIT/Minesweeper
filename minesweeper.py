import numpy as np

from board import Board
from difficulty import Difficulty
from difficulties import Difficulties
from location import Location
from status import Status
from tile import Tile

class Minesweeper:
    def __init__(self, difficulty: Difficulties):
        self.difficulty = difficulty
        self.board = Board(difficulty)
        self.moves = 0
        self.status = Status.IN_PROGRESS
        self.tiles_remaining = difficulty.value.height * difficulty.value.width

    def __str__(self) -> str:
        return f'Moves: {self.moves}\nDifficulty: {self.difficulty.value}\nTiles: {self.tiles_remaining}\n{self.board}'

    def play(self):
        while True:
            clear()
            print(self)
            move = input("Enter a coordinate x and y values separated by a space: ").split()
            x = int(move[0])
            y = int(move[1])
            self.make_move(x, y)

    def make_move(self, x: int, y: int):
        if self.board.tiles[y][x].is_flipped:
            return
        if self.moves == 0:
            self.board.populate(Location(x, y))
        self.board.tiles[y][x].flip()
        self.moves += 1
        self.tiles_remaining -= 1
        if self.board.tiles[y][x].is_bomb:
            self.status = Status.LOSS
        elif self.tiles_remaining == self.difficulty.value.bombs:
            self.status = Status.WIN


def clear():
    print("\033c\033[3J\033[2J\033[0m\033[H")


def weights_board(minesweeper: Minesweeper, bombs: list[Location]) -> Board:
    diffs = {(0, 1), (0, -1),
             (1, 0), (1, 1), (1, -1),
             (-1, 0), (-1, 1), (-1, -1)}

    weights = {}
    copy_board = minesweeper.board.deep_copy()
    for y, row in enumerate(copy_board.tiles):
        for x, tile in enumerate(row):
            if Location(x, y) in bombs:
                tile.is_flipped = True
                tile.is_bomb = True
                for neighbor in tile.neighbors:
                    if neighbor.is_flipped:
                        neighbor.hint -= 1
            weights[tile.coords] = 0

    for y, row in enumerate(copy_board.tiles):
        for x, tile in enumerate(row):
            if not tile.is_flipped:
                continue
            for loc in [tile.coords + diff for diff in diffs]:
                if loc.y >= copy_board.difficulty.height or loc.x >= copy_board.difficulty.width:
                    continue
                if loc.y < 0 or loc.x < 0:
                    continue
                if copy_board.tiles[loc.y][loc.x].is_flipped:
                    continue
                weights[loc] += tile.hint

    weight_b = Board(minesweeper.difficulty)
    weight_b.tiles = [[Tile(x, y, Location(x, y) in bombs, weights[Location(x, y)]) for x in range(copy_board.difficulty.width)] for y in range(copy_board.difficulty.height)]
    for y, row in enumerate(weight_b.tiles):
        for x, tile in enumerate(row):
            tile.is_flipped = True
    return weight_b


def probability_board(minesweeper: Minesweeper, bombs: list[Location] = []) -> Board:
    probabilities = {}
    zeroes = []
    copy_board = minesweeper.board.deep_copy()
    for y, row in enumerate(copy_board.tiles):
        for x, tile in enumerate(row):
            if Location(x, y) in bombs:
                tile.is_flipped = True
                tile.is_bomb = True
                for neighbor in tile.neighbors:
                    if neighbor.is_flipped:
                        neighbor.hint -= 1
            probabilities[tile.coords] = []

    for y, row in enumerate(copy_board.tiles):
        for x, tile in enumerate(row):
            if not tile.is_flipped:
                continue
            unflipped_neighbors = set()
            for neighbor in tile.neighbors:
                if not neighbor.is_flipped:
                    unflipped_neighbors.add(neighbor)
            for neighbor in unflipped_neighbors:
                if tile.hint <= 0:
                    continue
                for n2 in neighbor.neighbors:
                    if n2.hint == 0 and not n2.is_bomb and n2.is_flipped:
                        probabilities[neighbor.coords].append(0)
                        zeroes.append(neighbor.coords)
                        break
                probabilities[neighbor.coords].append(tile.hint / len(unflipped_neighbors))
                # print(f'{neighbor.coords}={probabilities[neighbor.coords]}')

    for loc, prob_list in probabilities.items():
        if 1 in prob_list:
            probabilities[loc] = 100
            continue
        probabilities[loc] = int(round(np.prod(prob_list), 2) * 100) if prob_list else 0

    diffs = {(0, 1), (0, -1),
             (1, 0), (1, 1), (1, -1),
             (-1, 0), (-1, 1), (-1, -1)}
    prob_b = Board(minesweeper.difficulty)
    prob_b.tiles = [[Tile(x, y, probabilities[Location(x, y)] == 100 or Location(x, y) in bombs, probabilities[Location(x, y)], True) for x in range(minesweeper.difficulty.value.width)] for y in range(minesweeper.difficulty.value.height)]
    for y, row in enumerate(prob_b.tiles):
        for x, tile in enumerate(row):
            for loc in (tile.coords + diff for diff in diffs):
                if loc.y >= prob_b.difficulty.height or loc.x >= prob_b.difficulty.width:
                    continue
                if loc.y < 0 or loc.x < 0:
                    continue
                neighbor = prob_b.tiles[loc.y][loc.x]
                tile.neighbors.add(neighbor)

    new_bombs = [loc for loc, prob in probabilities.items() if prob == 100]
    if bombs:
        return prob_b, bombs + new_bombs, zeroes
    elif new_bombs:
        return probability_board(minesweeper, new_bombs)
    else:
        return prob_b, new_bombs, zeros


game = Minesweeper(Difficulties.EASY)
game.make_move(3, 3)
print(game)

prev_moves = 0
bombs = []
while (len(bombs) < game.difficulty.value.bombs) and prev_moves != game.moves:
    print()
    p, bombs, zeros = probability_board(game)
    prev_moves = game.moves
    moves = [] + zeros
    for row in p.tiles:
        for tile in row:
            if tile.is_bomb:
                bomb = tile
                for bomb_neighbor in bomb.neighbors:
                    if bomb_neighbor.hint == 0 and not bomb_neighbor.is_bomb:
                        for n2 in bomb_neighbor.neighbors:
                            if game.board.tiles[n2.coords.y][n2.coords.x].is_flipped:
                                moves.append(Location(bomb_neighbor.coords.x, bomb_neighbor.coords.y))
                                break

    for move in moves:
        game.make_move(move.x, move.y)

    print(f'Bombs found: {len(bombs)}')
    print(p)
    print()
    print(game)
    input()

b = weights_board(game, bombs)
weights = {}
if len(bombs) < game.difficulty.value.bombs:
    for row in b.tiles:
        for tile in row:
            if not tile.is_bomb and tile.hint > 0:
                weights[tile.coords] = tile.hint
    weights = [[k, v] for k, v in sorted(weights.items(), key=lambda x: x[1], reverse=True)]
    next_bomb = weights[0][0]
    if len(weights) == 2 and weights[0][1] == 2:
        next_bomb = weights[-1][0]
    print(f'bomb_guess={next_bomb}')

    p, bombs, zeros = probability_board(game, bombs + [next_bomb])
    for row in p.tiles:
        for tile in row:
            if tile.is_bomb:
                bomb = tile
                for bomb_neighbor in bomb.neighbors:
                    if bomb_neighbor.hint == 0 and not bomb_neighbor.is_bomb:
                        for n2 in bomb_neighbor.neighbors:
                            if game.board.tiles[n2.coords.y][n2.coords.x].is_flipped:
                                moves.append(Location(bomb_neighbor.coords.x, bomb_neighbor.coords.y))
                                break

    for move in moves:
        game.make_move(move.x, move.y)

print()
print(p)
print()
print(game)
print()

for row in game.board.tiles:
    for tile in row:
        tile.is_flipped = True if tile.is_bomb else tile.is_flipped


print(game)
# print(str(game.status).split('.')[-1].lower().replace('_', ' '))
print(f'bombs found: {len(bombs)}')
print('win' if len(bombs) == game.difficulty.value.bombs else 'lose')

# TODO: ?
# refactor solving to functions

# 50:50 interaction when not a corner and tile up/down/left/right of bomb is blank with equal (hints active on that square)/2
