__author__ = 'James Dozier'

import Terraria
import random


class WorldGenerationException(Exception):
    def __init__(self, msg):
        self.message = msg
        Exception.__init__(self, 'WorldGenerationException: %s' % msg)


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

    def fill_dirt(self):
        """
        Fills in the layer between surface and underworld with dirt.
        :return:
        """
        dirt = Terraria.Tile()
        dirt.active = True
        dirt.tile_type = 0

        for x in range(0, self.world.header.x_tiles):
            for y in range(self.world.header.surface_level, 1000):
                self.world.map.map[x][y] = dirt.clone()

    @staticmethod
    def should_spawn_ore(n, density, total):
        """
        Returns a boolean on if an ore cluster should be spawned.
        :param n: Tile number in x column
        :param density:
        :param total:
        :return:
        """

        percent = ((n * density) / total) / 100

        return random.random() < percent

    def spawn_ore(self, ore_type, density):
        """
        Spawns ore across the world.
        :param ore_type:
        :param density:
        :return:
        """
        y_start = self.world.header.surface_level
        y_end = 1000  # TODO: Change. Temp Value.
        total = y_end - y_start

        tile = Terraria.Tile()
        tile.active = True
        tile.tile_type = ore_type

        for x in range(0, self.world.header.x_tiles):
            for y in range(y_start, y_end):
                n = y - y_start

                if self.should_spawn_ore(n, density, total):
                    print('Ore at: %s, %s' % (x, y))

                    self.world.map.map[x][y] = tile.clone()

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

    def add_sign(self, x, y, text, tile_type=55):
        """
        Add sign to Terraria World at (x, y) with text. Tile Type defaults to sign, can be changed to 85 for
        Grave Stone Marker
        :param x:
        :param y:
        :param text:
        :param tile_type:
        :return:
        """
        if tile_type != 55 or tile_type != 85:
            raise WorldGenerationException('Invalid tile type for sign creation: %s' % tile_type)

        sign = Terraria.Sign()

        sign.x = x
        sign.y = y
        sign.text = text

        self.world.signs.signs.append(sign)
        self.world.signs.total_signs += 1

        sign_tiles = [Terraria.Tile(), Terraria.Tile(), Terraria.Tile(), Terraria.Tile()]
        for s_tile in sign_tiles:
            s_tile.active = True
            s_tile.tile_type = tile_type

        if tile_type == 85:
            u = 180
            v = 0
        else:
            u = 0
            v = 0

        sign_tiles[0].u = u
        sign_tiles[0].v = v
        self.world.map.map[x][y] = sign_tiles[0]

        sign_tiles[1].u = u + 18
        sign_tiles[1].v = v
        self.world.map.map[x + 1][y] = sign_tiles[1]

        sign_tiles[2].u = u
        sign_tiles[2].v = v + 18
        self.world.map.map[x][y + 1] = sign_tiles[2]

        sign_tiles[3].u = u + 18
        sign_tiles[3].v = v + 18
        self.world.map.map[x + 1][y + 1] = sign_tiles[3]

        return sign