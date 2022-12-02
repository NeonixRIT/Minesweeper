from board import Board
from difficulty import Difficulty
from difficulties import Difficulties
from location import Location
from status import Status
from tile import Tile


def clear():
    print("\033c\033[3J\033[2J\033[0m\033[H")


def get_neighbor_locations(start: Location) -> tuple[Location]:
    diffs = {(0, 1), (0, -1),
             (1, 0), (1, 1), (1, -1), (-1, 0),
             (-1, 1), (-1, -1)}
    for loc in [start + diff for diff in diffs]:
        yield loc


def get_corner_locations(start: Location, quadrant: int) -> list[Location]:
    corners = {
        1: {(0, 1), (1, 1), (1, 0)},  # Upper Right
        2: {(-1, 0), (-1, 1), (0, 1)},  # Upper Left
        3: {(0, -1), (-1, -1), (-1, 0)},  # Lower Left
        4: {(1, 0), (1, -1), (0, -1)},  # Lower Right
    }

    for loc in [start + diff for diff in corners[quadrant]]:
        yield Location(loc[0], loc[1])


def tile_is_corner(tile: Tile) -> (bool, int):
    if len(tile.neighbors) == 0:
        raise ValueError('Tile has no neighbors')
    flipped_neighbor_coords = [neighbor.cords for neighbor in tile.neighbors if neighbor.is_flipped]
    for quadrant in range(1, 5):
        flipped_corner_tiles = [corner for corner in get_corner_locations(tile.coords, quadrant) if corner in flipped_neighbor_coords]
        if len(flipped_corner_tiles) == 3:
            return True, quadrant
    return False, 0


def tile_is_edge(tile: Tile) -> bool:
    if len(tile.neighbors) == 0:
        raise ValueError('Tile has no neighbors')
    flipped_neighbor_coords = [neighbor.coords for neighbor in tile.neighbors if neighbor.is_flipped]
    return len(flipped_neighbor_coords) > 0
