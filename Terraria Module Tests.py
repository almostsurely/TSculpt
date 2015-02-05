__author__ = 'James Dozier'

import unittest
import Terraria

class Terraria_Tests(unittest.TestCase):

    def test_pstring(self):
        self.assertEqual(Terraria.store_pstring('Test'), b'\x04Test')

    def test_tiles(self):

        #Row of Empty Tiles
        tile = Terraria.Tile()

        self.assertEqual(tile.generate_bytestring(64), b'@@')

        #Row Dirt Tiles
        tile = Terraria.Tile()
        tile.active = True
        tile.tile_type = 0

        self.assertEqual(tile.generate_bytestring(64), b'B\x00@')

        #Single Dirt Tile
        self.assertEqual(tile.generate_bytestring(0), b'\x02\x00')

        #Different Brick style
        tile = Terraria.Tile()
        tile.active = True
        tile.tile_type = 0
        tile.brick_style = 1

        self.assertEqual(tile.generate_bytestring(0), b'\x03\x10\x00')

        #Liquid in Empty Tile
        tile = Terraria.Tile()
        tile.liquid_type = 24
        tile.liquid_amount = 255

        self.assertEqual(tile.generate_bytestring(0), b'\x18\xff')

        tile = Terraria.Tile()

        #Tile ID > 255
        tile.active = True
        tile.tile_type = 256

        self.assertEqual(tile.generate_bytestring(0), b'\x22\x00\x01')

        #Actuator Tile
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 0
        tile.actuator = True
        tile.actuator_inactive = True

        self.assertEqual(tile.generate_bytestring(2), b'\x43\x01\x06\x00\x02')

        #Wall Tile
        tile = Terraria.Tile()

        tile.wall = 5

        self.assertEqual(tile.generate_bytestring(0), b'\x04\x05')

        #Wired Tile
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 16
        tile.wire_red = True

        self.assertEqual(tile.generate_bytestring(0), b'\x03\x02\x10')

        #U and V Tiles
        tile = Terraria.Tile()

        tile.active = True
        tile.tile_type = 28
        tile.u = 18
        tile.v = 108

        self.assertEqual(tile.generate_bytestring(0), b'\x02\x1C\x12\x00\x6C\x00')

        #Tile Clone and Equals check
        clone = tile.clone()

        self.assertEqual(clone, tile)
        self.assertTrue(clone == tile)

if __name__ == '__main__':
    unittest.main()