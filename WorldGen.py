__author__ = 'James Dozier'

import Terraria

class WorldGenerator():
    """
    Main class that generates worlds.
    """

    def __init__(self, world):
        """
        Initializes the Generator
        :param world: Terraria.World object
        :return:
        """
        self.world = world

    def add_chest(self, x, y):
        """
        Adds a chest at the x, y location. Returns chest for Item Generation.
        :param x:
        :param y:
        :return: chest
        """

        chest = Terraria.Chest()

        chest.x = x
        chest.y = y
        item = [0, None, None]
        chest.items = [item] * self.world.chests.max_items

        self.world.chests.chests.append(chest)

        chest_tiles = [Terraria.Tile(), Terraria.Tile(), Terraria.Tile(), Terraria.Tile()]

        for tile in chest_tiles:
            tile.active = True
            tile.tile_type = 21

        chest_tiles[0].u = 612
        chest_tiles[0].v = 0
        self.world.map.map[x][y] = chest_tiles[0]

        chest_tiles[1].u = 630
        chest_tiles[1].v = 0
        self.world.map.map[x + 1][y] = chest_tiles[1]

        chest_tiles[2].u = 612
        chest_tiles[2].v = 18
        self.world.map.map[x][y + 1] = chest_tiles[2]

        chest_tiles[3].u = 630
        chest_tiles[3].v = 18
        self.world.map.map[x + 1][y + 1] = chest_tiles[3]

        self.world.chests.total_chests += 1

        return chest