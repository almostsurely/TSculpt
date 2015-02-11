__author__ = 'James Dozier'

import unittest
import Terraria
import WorldGen
import random

class TSculpt_Tests(unittest.TestCase):

    def test_pstring(self):
        self.assertEqual(Terraria.store_pstring('Test'), b'\x04Test')

    def test_world(self):
        world = Terraria.World()

        self.assertTrue(world.header.validate())
        self.assertTrue(world.map.validate())
        self.assertTrue(world.chests.validate())
        self.assertTrue(world.signs.validate())
        self.assertTrue(world.npcs.validate())
        self.assertTrue(world.footer.validate())
        self.assertTrue(world.validate())



    def test_tiles(self):
        #Tile Importance from a 1.2.4.1 world
        tile_importance = [
            False, False, False, True, True, True, False, False, False, False, True, True, True, True, True, True,
            True, True, True, True, True, True, False, False, True, False, True, True, True, True, False, True, False,
            True, True, True, True, False, False, False, False, False, True, False, False, False, False, False, False,
            False, True, False, False, False, False, True, False, False, False, False, False, True, False, False,
            False, False, False, False, False, False, False, True, True, True, True, False, False, True, True, True,
            False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
            True, True, True, True, True, True, True, True, True, True, False, False, False, True, False, False, True,
            True, False, False, False, False, False, False, False, False, False, False, True, True, False, True, True,
            False, False, True, True, True, True, True, True, True, True, False, True, True, True, True, False, False,
            False, False, True, False, False, False, False, False, False, False, False, False, False, False, False,
            False, False, False, True, False, False, False, False, False, True, False, True, True, False, False, False,
            True, False, False, False, False, False, True, True, True, True, False, False, False, False, False, False,
            False, False, False, False, False, False, False, True, False, False, False, False, False, True, False,
            True, True, False, True, False, False, True, True, True, True, True, True, False, False, False, False,
            False, False, True, True, False, False, True, False, True, False, True, True, True, True, True, True,
            True, True, True, True, True, True, True, False, False, False, False, False, False, True, False, False,
            False, False, False, False, False, False, False, False, False, False, False, False, True, True, True,
            False, False, False, True, True, True, True, True, True, True, True, True, False, True, True, True, True,
            True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
            True, True, True, True, False, False, False, True, False, True, True, True, True, True, False, False, True,
            True, False, False, False, False, False, False, False, False, False, True, True, False, True, True, True
        ]


        #Row of Empty Tiles
        tile = Terraria.Tile()

        self.assertEqual(tile.generate_bytestring(64, tile_importance), b'@@')

        #Row Dirt Tiles
        tile = Terraria.Tile()
        tile.active = True
        tile.tile_type = 0

        self.assertEqual(tile.generate_bytestring(64, tile_importance), b'B\x00@')

        #Single Dirt Tile
        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x02\x00')

        #Different Brick style
        tile = Terraria.Tile()
        tile.active = True
        tile.tile_type = 0
        tile.brick_style = 1

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x03\x10\x00')

        #Liquid in Empty Tile
        tile = Terraria.Tile()
        tile.liquid_type = 24
        tile.liquid_amount = 255

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x18\xff')

        tile = Terraria.Tile()

        #Tile ID > 255
        tile.active = True
        tile.tile_type = 256

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x22\x00\x01')

        #Actuator Tile
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 0
        tile.actuator = True
        tile.actuator_inactive = True

        self.assertEqual(tile.generate_bytestring(2, tile_importance), b'\x43\x01\x06\x00\x02')

        #Wall Tile
        tile = Terraria.Tile()

        tile.wall = 5

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x04\x05')

        #Wired Tile
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 0
        tile.wire_red = True

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x03\x02\x00')

        #U and V Tiles
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 28
        tile.u = 18
        tile.v = 108

        self.assertEqual(tile.generate_bytestring(0, tile_importance), b'\x02\x1C\x12\x00\x6C\x00')

        #Tile Clone and Equals check
        clone = tile.clone()

        self.assertEqual(clone, tile)
        self.assertTrue(clone == tile)

    def test_world_generation(self):
        """
        Test the World generation script
        :return:
        """
        world = Terraria.World()
        worldgen = WorldGen.WorldGenerator(world)

        #Assert raises exception for wrong Tile_Type for adding signs.
        self.assertRaises(WorldGen.WorldGenerationException, worldgen.add_sign, 0, 0, 'Test', 44)

        #Assert that dirt was filled out in underground
        worldgen.fill_dirt()

        test_y = random.randint(world.header.surface_level, 1000)
        test_x = random.randint(0, 4200)
        self.assertTrue(world.map.map[test_x][test_y].tile_type == 0)

if __name__ == '__main__':
    unittest.main()