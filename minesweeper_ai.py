import time

import numpy as np

from alive_progress import alive_bar

from board import Board
from colors import Colors
from difficulties import Difficulties
from location import Location
from minesweeper import Minesweeper
from multiprocessing import Process, Queue
from status import Status
from threading import Thread
from tile import Tile
from utils import get_neighbor_locations, tile_is_edge


def get_next_moves(game, bombs, is_guess: bool = False) -> list[Location]:
    pb, bombs, zeroes, base_hint = probability_board(game, bombs)

    moves = []
    for row in pb.tiles:
        for tile in row:
            if not tile.is_bomb:
                continue
            bomb = tile
            for bomb_neighbor in bomb.neighbors:
                if bomb_neighbor.hint == base_hint or bomb_neighbor.is_bomb or bomb_neighbor.coords in moves:
                    continue

                game_tile = game.board.tiles[bomb_neighbor.coords.y][bomb_neighbor.coords.x]
                # print('Hints: ', [t.hint for t in game_tile.neighbors if t.is_flipped])
                if tile_is_edge(game_tile) and not game_tile.is_flipped and [t for t in game_tile.neighbors if t.hint <= 1 and t.is_flipped and not pb.tiles[t.coords.y][t.coords.x].is_bomb and t in bomb.neighbors]:
                    moves.append(bomb_neighbor.coords)
                    break

        wb = weights_board(game, bombs)

        # print()
        # print(wb)
        # print()
        # print()
        # print(pb)
        # print()

        # print([str(z) for z in zeroes])
        # print([str(m) for m in moves])

        moves = set(moves) | set(zeroes)
        if is_guess:
            moves = moves ^ zeroes
        if moves:
            return [moves.pop()] if is_guess else moves
        if zeroes:
            return [zeroes.pop()]
        if is_guess:
            x = np.random.randint(0, game.difficulty.value.width)
            y = np.random.randint(0, game.difficulty.value.height)
            while game.board.tiles[y][x].is_flipped or pb.tiles[y][x].is_bomb or not tile_is_edge(game.board.tiles[y][x]):
                x = np.random.randint(0, game.difficulty.value.width)
                y = np.random.randint(0, game.difficulty.value.height)
            return [Location(x, y)]
        return []


def attempt_solve_probability(game: Minesweeper, bombs: list[Location] = None, bomb_guess: Location = None) -> (Status, list[Location]):
    if bombs is None:
        bombs = []

    if bomb_guess is not None:
        bombs.append(bomb_guess)

    if game.moves == 0:
        x = np.random.randint(0, game.difficulty.value.width)
        y = np.random.randint(0, game.difficulty.value.height)
        game.make_move(x, y)
        # print(f'First Move: ({x}, {y})')
        # print(game)
        # print()

    iteration = 0
    prev_bomb_guess = None
    while game.status == Status.IN_PROGRESS:

        # print(game.board)
        # print()
        # print(wb)
        # print()
        # print(pb)
        # print()

        prev_moves = game.moves
        moves = get_next_moves(game, bombs, bomb_guess is not None)
        # print(f'Iteration: {iteration}\n  Bomb Guess: {bomb_guess}\n  Moves: {[str(loc) for loc in moves]}.\n  Bombs: {[str(loc) for loc in bombs]}')
        if not moves and prev_bomb_guess is not None:
            break
        for move in moves:
            game.make_move(move.x, move.y)
            if bomb_guess is not None:
                # print(str(move))
                break

        # print(game.board)
        # print()

        if bomb_guess is not None:
            bombs.remove(bomb_guess)
            prev_bomb_guess = bomb_guess
            bomb_guess = None

        if prev_moves == game.moves:
            return game.status, bombs
        iteration += 1
    return game.status, bombs


def attempt_solve(game: Minesweeper) -> bool:
    bomb_guesses = []
    bombs = []
    bomb_guess = None
    while game.status == Status.IN_PROGRESS and len(bombs) < game.difficulty.value.bombs:
        _, bombs = attempt_solve_probability(game, bombs, bomb_guess)
        for bomb in bomb_guesses:
            if bomb in bombs:
                bomb_guesses.remove(bomb)

        if game.status == Status.IN_PROGRESS:
            pb, bombs, zeroes, base_hint = probability_board(game, bombs)
            if len(bombs) == game.difficulty.value.bombs:
                break
            # print('Equal Probability Found, attempting guess')
            bomb_guess = guess_next_bomb(game, pb, base_hint, bombs, bomb_guesses)
            if bomb_guess is None:
                # print('No guess found')
                continue
            bomb_guesses.append(bomb_guess)
            color = Colors.RED.value if not game.board.tiles[bomb_guess.y][bomb_guess.x].is_bomb else Colors.GREEN.value
            text = 'WRONG' if not game.board.tiles[bomb_guess.y][bomb_guess.x].is_bomb else 'CORRECT'
            # print(f'{color}{text}: {bomb_guess}{Colors.WHITE.value}')

    if len(bombs) == game.difficulty.value.bombs:
        for row in game.board.tiles:
            for tile in row:
                if tile.coords not in bombs:
                    game.make_move(tile.coords.x, tile.coords.y)

    # print(str(game.status).split('.')[-1].lower().replace('_', ' '))
    # game.board.reveal_bombs()
    # print(game)
    return game.status == Status.WIN


def sub_hints_known_bombs(tiles: list[Tile], bombs: list[Location]):
    for i, tile in enumerate(tiles):
        if tile.coords in bombs:
            tile.is_flipped = True
            tile.is_bomb = True
            for neighbor in tile.neighbors:
                if neighbor.is_flipped:
                    neighbor.hint -= 1


def weights_board(minesweeper: Minesweeper, bombs: list[Location] = None) -> Board:
    if bombs is None:
        bombs = []

    copy_board = minesweeper.board.copy()
    tiles = np.array(copy_board.tiles).flatten()
    sub_hints_known_bombs(tiles, bombs)

    weights = {t.coords: 0 for t in tiles}
    for tile in tiles:
        if not tile.is_flipped:
            continue
        for neighbor in [n for n in tile.neighbors if not n.is_flipped]:
            weights[neighbor.coords] += tile.hint

    weight_b = Board(minesweeper.difficulty)
    weight_b.tiles = [[Tile(x, y, Location(x, y) in bombs, weights[Location(x, y)], True) for x in range(copy_board.difficulty.width)] for y in range(copy_board.difficulty.height)]
    return weight_b


def probability_board(minesweeper: Minesweeper, bombs: list[Location] = None) -> (Board, list, list, int):
    if bombs is None:
        bombs = []

    copy_board = minesweeper.board.copy()
    tiles = np.array(copy_board.tiles).flatten()
    sub_hints_known_bombs(tiles, bombs)

    zeroes = []
    diff = minesweeper.difficulty.value
    base_full = (diff.bombs - len(bombs)) / (diff.height * diff.width)
    base_hint = round(base_full, 4) * 100
    probabilities = {tile.coords: [base_full if not tile.is_flipped else 0] for tile in tiles}
    if len(bombs) >= diff.bombs:
        probabilities = {tile.coords: [] for tile in tiles}
    for tile in [tile for tile in tiles if tile.is_flipped and tile.hint > 0]:
        unflipped_neighbors = [n for n in tile.neighbors if not n.is_flipped and not n.is_bomb]
        for neighbor in unflipped_neighbors:
            for n2 in neighbor.neighbors:
                if n2.hint == 0 and not n2.is_bomb and n2.is_flipped:
                    probabilities[neighbor.coords].append(0)
                    zeroes.append(neighbor.coords)
                    break
            probabilities[neighbor.coords].append(tile.hint / len(unflipped_neighbors))
    # print(f'Zeroes_1: {[str(loc) for loc in zeroes]}')
    # for k, v in probabilities.items():
    #     if v[0] == 0 and len(v) == 1:
    #         continue
    #     print(f'{k}: {v} ({round(np.prod(v), 4) * 100 if v else 0})')

    for loc, prob_list in probabilities.items():
        if 1 in prob_list:
            probabilities[loc] = 100
            continue
        probabilities[loc] = round(np.prod(prob_list), 4) * 100 if prob_list else 0

    prob_b = Board(minesweeper.difficulty)
    prob_b.tiles = [[Tile(x, y, probabilities[Location(x, y)] == 100 or Location(x, y) in bombs, probabilities[Location(x, y)], True) for x in range(minesweeper.difficulty.value.width)] for y in range(minesweeper.difficulty.value.height)]
    for y, row in enumerate(prob_b.tiles):
        for x, tile in enumerate(row):
            for loc in get_neighbor_locations(Location(x, y)):
                if not minesweeper.in_bounds(loc):
                    continue
                neighbor = prob_b.tiles[loc.y][loc.x]
                tile.neighbors.add(neighbor)

    for row in prob_b.tiles:
        for tile in row:
            if not tile.is_bomb:
                continue
            for n2 in tile.neighbors:
                game_tile = copy_board.tiles[n2.coords.y][n2.coords.x]
                if game_tile.is_flipped and game_tile.hint == 0:
                    for l2 in [tile.coords for tile in game_tile.neighbors if not game_tile.is_bomb and not game_tile.is_flipped]:
                        zeroes.append(l2)
                        probabilities[l2] = 0

    # print(f'Zeroes_2: {[str(loc) for loc in zeroes]}')
    new_bombs = [loc for loc, prob in probabilities.items() if prob == 100]
    for row in prob_b.tiles:
        for tile in row:
            if tile.hint <= 0 or tile.is_bomb:
                continue

    if bombs:
        return prob_b, bombs + new_bombs, set(zeroes), base_hint
    elif new_bombs:
        return probability_board(minesweeper, new_bombs)
    else:
        return prob_b, new_bombs, set(zeroes), base_hint


def guess_next_bomb(game: Minesweeper, prob_board: Board, base_hint, bombs: list[Location], bomb_guesses) -> Location | None:
    old_weights = {}
    new_weights = {}
    weight_board = weights_board(game, bombs)

    # print()
    # print(weight_board)
    # print()
    # print(prob_board)
    # print()
    clusters = sorted(find_clusters(prob_board, weight_board, base_hint), key=lambda x: len(x) - sum([prob_board.tiles[t.y][t.x].hint for t in x]))
    if not clusters:
        return

    smallest_cluster = clusters[0]
    largest_cluster = clusters[-1]
    for i, cluster in enumerate(clusters):
        for loc in cluster:
            prob_tile = prob_board.tiles[loc.y][loc.x]
            weight_tile = weight_board.tiles[loc.y][loc.x]
            if not weight_tile.is_bomb and weight_tile.hint > 0:
                old_weights[weight_tile.coords] = weight_tile.hint
            if prob_tile.hint <= 0 or weight_tile.hint <= 0 or prob_tile.is_bomb:
                continue
            new_weight = prob_tile.hint * weight_tile.hint
            new_weights[prob_tile.coords] = new_weight

        if len(new_weights) > 0:
            break

    new_weights = {k: v for k, v in sorted(new_weights.items(), key=lambda x: x[1], reverse=True)}
    for bomb in bomb_guesses:
        if bomb in new_weights:
            del new_weights[bomb]

    filtered_clusters = []
    for i, cluster in enumerate(clusters):
        for bomb in bomb_guesses:
            if bomb in cluster:
                cluster = cluster ^ {bomb}
        if cluster:
            filtered_clusters.append(cluster)

    if new_weights:
        return list(new_weights.items())[0][0]
    if len(filtered_clusters) > 0:
        return list(filtered_clusters[np.random.randint(0, len(filtered_clusters))])[0]
    x = np.random.randint(0, game.difficulty.value.width)
    y = np.random.randint(0, game.difficulty.value.height)
    while game.board.tiles[y][x].is_flipped or prob_board.tiles[y][x].is_bomb or not tile_is_edge(game.board.tiles[y][x]):
        x = np.random.randint(0, game.difficulty.value.width)
        y = np.random.randint(0, game.difficulty.value.height)
    return Location(x, y)


def find_cluster(pb: Board, wb: Board, loc: Location, base_hint: int, cluster: tuple[Location] = None) -> tuple[Location]:
    if cluster is None:
        cluster = tuple()

    if loc not in cluster:
        cluster += tuple([loc])

    new_hint_neighbors = tuple([t.coords for t in pb.tiles[loc.y][loc.x].neighbors if t.hint > 0 and t.hint != base_hint and not t.is_bomb and t.coords not in cluster and wb.tiles[t.coords.y][t.coords.x].hint > 0])
    if not new_hint_neighbors:
        return cluster
    cluster += new_hint_neighbors

    return find_cluster(pb, wb, new_hint_neighbors[-1], base_hint, cluster)


def filter_clusters(clusters):
    filtered = []
    for i, clust_1 in enumerate(clusters):
        skip = False
        for j, clust_2 in enumerate(clusters):
            if i == j:
                continue
            if len(clust_1 & clust_2) > 0:
                if clust_1 | clust_2 not in filtered:
                    filtered.append(clust_1 | clust_2)
                skip = True
                break
            if clust_1 >= clust_2:
                filtered.append(clust_1 | clust_2)
                skip = True
                break
            if clust_1 <= clust_2:
                skip = True
                break
        if clust_1 not in filtered and not skip:
            filtered.append(clust_1)
    return filtered


def find_clusters(pb: Board, wb: Board, base_hint):
    clusters = []
    for prob_row, weight_row in zip(pb.tiles, wb.tiles):
        for prob_tile, weight_tile in zip(prob_row, weight_row):
            if prob_tile.hint <= 0 or prob_tile.is_bomb:
                continue
            cluster = set(find_cluster(pb, wb, prob_tile.coords, base_hint))
            if cluster not in clusters:
                clusters.append(cluster)

    filtered_1 = filter_clusters(sorted(clusters, key=lambda x: len(x), reverse=True))
    filtered_2 = filter_clusters(sorted(filtered_1, key=lambda x: len(x), reverse=True))
    return filtered_2


def test_winrate_threaded(games: int, threads: int, difficulty: Difficulties) -> int:
    with alive_bar(games, force_tty=True) as bar:
        results = []
        games_per_thread = games // threads

        join_list = []

        def run():
            for _ in range(games_per_thread):
                game = Minesweeper(difficulty)
                win = attempt_solve(game)
                results.append(int(win))
                bar()

        for _ in range(threads):
            thread = Thread(target=run)
            join_list.append(thread)

        for thread in join_list:
            thread.start()

        for thread in join_list:
            thread.join()

    return sum(results) / games * 100


def run(games_per_thread, difficulty, results):
    for i in range(games_per_thread):
        game = Minesweeper(difficulty)
        win = attempt_solve(game)
        results.put(int(win))


def test_winrate_multipoc(games: int, count: int, difficulty: Difficulties) -> int:
    results = Queue()
    games_per_thread = games // count

    procs = [Process(target=run, args=(games_per_thread, difficulty, results)) for _ in range(count)]
    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()

    return sum([results.get() for _ in range(games_per_thread * count)]) / (games_per_thread * count) * 100


def main():
    wins = 0
    games = 300
    with alive_bar(games, force_tty=True) as bar:
        for _ in range(games):
            game = Minesweeper(Difficulties.EASY)
            win = attempt_solve(game)
            wins += win
            bar()
    print(wins / games * 100)

    # game = Minesweeper(Difficulties.EASY)
    # print(game)
    # attempt_solve(game)
    # print(game)
    # print()
    # game.board.reveal_bombs()
    # print(game.board)
    # print(game.status)

    # print(game)
    # print()
    # pb, _, _, _ = probability_board(game)
    # print(pb)
    # print()
    # game.board.reveal_bombs()
    # print(game.board)


    # time_per_game = 0.05  # 4 count
    # games = 10
    # print(f'Estimated Time: {games * time_per_game} seconds.')
    # start = time.perf_counter()
    # print(f'Winrate: {test_winrate_multipoc(games, 4, Difficulties.EASY)}')
    # stop = time.perf_counter()
    # print(f'Total Time: {stop - start} seconds.')

    # winerates = {}
    # with alive_bar(5000 * 100, force_tty=True) as bar:
    #     for i in range(101):
    #         wins = 0
    #         games = 5000
    #         for _ in range(games):
    #             game = Minesweeper(Difficulties.EASY)
    #             game.make_move(3, 3)
    #
    #             prob_board, bombs, _ = probability_board(game)
    #             next_bomb = guess_next_bomb(game, prob_board, bombs, 163)
    #             if next_bomb is not None:
    #                 if game.board.tiles[next_bomb.y][next_bomb.x].is_bomb:
    #                     wins += 1
    #             bar()
    #         winrate = round((wins / games) * 100, 2)
    #         winerates[i] = winrate
    #
    # print(winerates)
    #
    # import json
    # with open('winrates.json', 'r') as file:
    #     # json.dump(winerates, file)
    #     data = json.load(file)
    #
    # print({k: v for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)})


if __name__ == '__main__':
    main()
