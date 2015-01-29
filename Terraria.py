__author__ = 'James Dozier'

from struct import *


def get_pstring(f):
    """
    Get a pstring value from file (f)
    :param f:
    :return: value from pstring
    """
    length = unpack('<B', f.read(1))[0]
    string = unpack('s' * length, f.read(length))

    return ''.join([c.decode() for c in string])


class WorldFormatException(Exception):
    def __init__(self, msg):
        self.message = msg
        Exception.__init__(self, 'WorldFormatException: %s' % msg)


class World:
    """
    World Object for Terraria.
    """

    min_version = 102  # Minimum world version this application is designed to handle.

    def __init__(self):
        """
        Initializes the World Object.
        :return:
        """

        self.version = None
        self.section_count = None
        self.section_pointers = ()
        self.tile_type_count = None
        self.tile_importance = []

        self.header = Header()
        self.map = Map()
        self.chests = Chests()

    def load_world(self, f):
        """
        Loads the World from file (f).
        :param f:
        :return:
        """

        self.version = unpack('<i', f.read(4))[0]

        if self.version < World.min_version:
            raise WorldFormatException('World version %i is below minimally supported version of %i.' %
                                       (self.version, World.min_version))

        self.section_count = unpack('<h', f.read(2))[0]
        self.section_pointers = unpack('i' * self.section_count, f.read(self.section_count * 4))
        self.tile_type_count = unpack('<h', f.read(2))[0]

        self.tile_importance = []
        mask = 0x80
        flags = 0
        for i in range(0, self.tile_type_count):
            if mask == 0x80:
                mask = 0x01
                flags = unpack('<B', f.read(1))[0]
            else:
                mask <<= 1

            if flags & mask != 0:
                self.tile_importance.append(True)
            else:
                self.tile_importance.append(False)

        if f.tell() != self.section_pointers[0]:
            raise WorldFormatException('Header location off from section pointer.')

        self.header.load_header(f, self.section_pointers[0])

        if f.tell() != self.section_pointers[1]:
            raise WorldFormatException('Map location off from section pointer.')

        self.map.load_map(f, self.section_pointers[1], self.header.x_tiles, self.header.y_tiles, self.tile_importance)

        if f.tell() != self.section_pointers[2]:
            raise WorldFormatException('Chest location off from section pointer.')

        self.chests.load_chests(f, self.section_pointers[2])

        if f.tell() != self.section_pointers[3]:
            raise WorldFormatException('Sign location off from section pointer.')


class Header:
    """
    Header of the Terraria World Object.
    """

    def __init__(self):
        """
        Initializes the Header Object.
        :return:
        """

        self.world_name = 'Default'
        self.world_id = None
        self.x = None
        self.w = None
        self.y = None
        self.h = None
        self.y_tiles = None
        self.x_tiles = None
        self.moon_type = None
        self.tree_x = None
        self.tree_style = None
        self.cave_back_x = None
        self.cave_back_style = None
        self.ice_back_style = None
        self.jungle_back_style = None
        self.hell_back_style = None
        self.spawn_x = None
        self.spawn_y = None
        self.surface_level = None
        self.rock_layer = None
        self.temp_time = None
        self.is_day = None
        self.moon_phase = None
        self.is_blood_moon = None
        self.is_eclipse = None
        self.dungeon_x = None
        self.dungeon_y = None
        self.is_crimson = None
        self.is_boss_1_dead = None
        self.is_boss_2_dead = None
        self.is_boss_3_dead = None
        self.is_queen_bee_dead = None
        self.is_mech_1_dead = None
        self.is_mech_2_dead = None
        self.is_mech_3_dead = None
        self.is_any_mech_dead = None
        self.is_plant_dead = None
        self.is_golem_dead = None
        self.is_goblin_saved = None
        self.is_wizard_saved = None
        self.is_mechanic_saved = None
        self.is_goblins_beat = None
        self.is_clown_beat = None
        self.is_frost_beat = None
        self.is_pirates_beat = None
        self.is_orb_smashed = None
        self.is_meteor_spawned = None
        self.orb_smash_count = None
        self.altar_count = None
        self.is_hard_mode = None
        self.invasion_delay = None
        self.invasion_size = None
        self.invasion_type = None
        self.invasion_x = None
        self.is_temp_raining = None
        self.temp_rain_time = None
        self.temp_max_rain = None
        self.ore_tier_1 = None
        self.ore_tier_2 = None
        self.ore_tier_3 = None
        self.bg_tree = None
        self.bg_corruption = None
        self.bg_jungle = None
        self.bg_snow = None
        self.bg_hallow = None
        self.bg_crimson = None
        self.bg_desert = None
        self.bg_ocean = None
        self.cloud_bg_active = None
        self.num_clouds = None
        self.wind_speed_set = None
        self.num_anglers = None
        self.is_angler_saved = None
        self.angler_quest = None

    def load_header(self, f, index):
        """
        Loads the Header starting at (index) in file (f).
        :param f:
        :param index:
        :return:
        """

        f.seek(index)

        self.world_name = get_pstring(f)
        self.world_id = unpack('<i', f.read(4))[0]
        self.x = unpack('<i', f.read(4))[0]
        self.w = unpack('<i', f.read(4))[0]
        self.y = unpack('<i', f.read(4))[0]
        self.h = unpack('<i', f.read(4))[0]
        self.y_tiles = unpack('<i', f.read(4))[0]
        self.x_tiles = unpack('<i', f.read(4))[0]
        self.moon_type = unpack('<B', f.read(1))[0]
        self.tree_x = unpack('<iii', f.read(12))
        self.tree_style = unpack('<iiii', f.read(16))
        self.cave_back_x = unpack('<iii', f.read(12))
        self.cave_back_style = unpack('<iiii', f.read(16))
        self.ice_back_style = unpack('<i', f.read(4))[0]
        self.jungle_back_style = unpack('<i', f.read(4))[0]
        self.hell_back_style = unpack('<i', f.read(4))[0]
        self.spawn_x = unpack('<i', f.read(4))[0]
        self.spawn_y = unpack('<i', f.read(4))[0]
        self.surface_level = unpack('<d', f.read(8))[0]
        self.rock_layer = unpack('<d', f.read(8))[0]
        self.temp_time = unpack('<d', f.read(8))[0]
        self.is_day = unpack('<?', f.read(1))[0]
        self.moon_phase = unpack('<i', f.read(4))[0]
        self.is_blood_moon = unpack('<?', f.read(1))[0]
        self.is_eclipse = unpack('<?', f.read(1))[0]
        self.dungeon_x = unpack('<i', f.read(4))[0]
        self.dungeon_y = unpack('<i', f.read(4))[0]
        self.is_crimson = unpack('<?', f.read(1))[0]
        self.is_boss_1_dead = unpack('<?', f.read(1))[0]
        self.is_boss_2_dead = unpack('<?', f.read(1))[0]
        self.is_boss_3_dead = unpack('<?', f.read(1))[0]
        self.is_queen_bee_dead = unpack('<?', f.read(1))[0]
        self.is_mech_1_dead = unpack('<?', f.read(1))[0]
        self.is_mech_2_dead = unpack('<?', f.read(1))[0]
        self.is_mech_3_dead = unpack('<?', f.read(1))[0]
        self.is_any_mech_dead = unpack('<?', f.read(1))[0]
        self.is_plant_dead = unpack('<?', f.read(1))[0]
        self.is_golem_dead = unpack('<?', f.read(1))[0]
        self.is_goblin_saved = unpack('<?', f.read(1))[0]
        self.is_wizard_saved = unpack('<?', f.read(1))[0]
        self.is_mechanic_saved = unpack('<?', f.read(1))[0]
        self.is_goblins_beat = unpack('<?', f.read(1))[0]
        self.is_clown_beat = unpack('<?', f.read(1))[0]
        self.is_frost_beat = unpack('<?', f.read(1))[0]
        self.is_pirates_beat = unpack('<?', f.read(1))[0]
        self.is_orb_smashed = unpack('<?', f.read(1))[0]
        self.is_meteor_spawned = unpack('<?', f.read(1))[0]
        self.orb_smash_count = unpack('<B', f.read(1))[0]
        self.altar_count = unpack('<i', f.read(4))[0]
        self.is_hard_mode = unpack('<?', f.read(1))[0]
        self.invasion_delay = unpack('<i', f.read(4))[0]
        self.invasion_size = unpack('<i', f.read(4))[0]
        self.invasion_type = unpack('<i', f.read(4))[0]
        self.invasion_x = unpack('<d', f.read(8))[0]
        self.is_temp_raining = unpack('<?', f.read(1))[0]
        self.temp_rain_time = unpack('<i', f.read(4))[0]
        self.temp_max_rain = unpack('<f', f.read(4))[0]
        self.ore_tier_1 = unpack('<i', f.read(4))[0]
        self.ore_tier_2 = unpack('<i', f.read(4))[0]
        self.ore_tier_3 = unpack('<i', f.read(4))[0]
        self.bg_tree = unpack('<B', f.read(1))[0]
        self.bg_corruption = unpack('<B', f.read(1))[0]
        self.bg_jungle = unpack('<B', f.read(1))[0]
        self.bg_snow = unpack('<B', f.read(1))[0]
        self.bg_hallow = unpack('<B', f.read(1))[0]
        self.bg_crimson = unpack('<B', f.read(1))[0]
        self.bg_desert = unpack('<B', f.read(1))[0]
        self.bg_ocean = unpack('<B', f.read(1))[0]
        self.cloud_bg_active = unpack('<i', f.read(4))[0]
        self.num_clouds = unpack('<h', f.read(2))[0]
        self.wind_speed_set = unpack('<f', f.read(4))[0]
        self.num_anglers = unpack('<i', f.read(4))[0]
        self.is_angler_saved = unpack('<?', f.read(1))[0]
        self.angler_quest = unpack('<i', f.read(4))[0]


class Map():
    """
    Object representing a map in Terraria
    """

    def __init__(self):
        """
        Initializes the Map Object
        :return:
        """

        self.x_tiles = 0
        self.y_tiles = 0
        self.map = []

    def load_map(self, f, index, x_tiles, y_tiles, tile_importance):
        """
        Loads the Map from file (f) starting at (index)
        :param f:
        :param index:
        :param x_tiles:
        :param y_tiles:
        :param tile_importance:
        :return:
        """

        self.x_tiles = x_tiles
        self.y_tiles = y_tiles

        f.seek(index)
        for x in range(0, self.x_tiles):
            self.map.append([])

            rle = 0

            tile = None

            for y in range(0, self.y_tiles):

                if rle > 0:
                    self.map[x].append(tile.clone())
                    rle -= 1
                    continue

                tile = Tile()

                header_1 = unpack('<B', f.read(1))[0]
                header_2 = 0
                header_3 = 0

                if header_1 & 1 == 1:
                    header_2 = unpack('<B', f.read(1))[0]

                    if header_2 & 1 == 1:
                        header_3 = unpack('<B', f.read(1))[0]

                if header_1 & 2 == 2:
                    if (header_1 & 32) != 32:
                        tile.tile_type = unpack('<B', f.read(1))[0]
                    else:
                        lower_byte = unpack('<B', f.read(1))[0]
                        upper_byte = unpack('<B', f.read(1))[0]
                        tile.tile_type = (upper_byte << 8) | lower_byte

                    if not tile_importance[tile.tile_type]:
                        tile.u = -1
                        tile.v = -1
                    else:
                        tile.u = unpack('<h', f.read(2))[0]
                        tile.v = unpack('<h', f.read(2))[0]

                    if header_3 & 8 == 8:
                        tile.color = unpack('<B', f.read(1))[0]

                if header_1 & 4 == 4:
                    tile.wall = unpack('<B', f.read(1))[0]

                    if header_3 & 16 == 16:
                        tile.wall_color = unpack('<B', f.read(1))[0]

                tile.liquid_type = header_1 & 24

                if tile.liquid_type != 0:

                    tile.liquid_amount = unpack('<B', f.read(1))[0]

                if header_2 > 1:
                    if header_2 & 2 == 2:
                        tile.wire_red = True
                    if header_2 & 4 == 4:
                        tile.wire_green = True
                    if header_2 & 8 == 8:
                        tile.wire_blue = True

                    tile.brick_style = (header_2 & 112) >> 4

                if header_3 > 0:
                    if header_3 & 2 == 2:
                        tile.actuator = True
                    if header_3 & 4 == 4:
                        tile.act_inactive = True

                rle_type = (header_1 & 192) >> 6

                if rle_type == 0:
                    rle = 0
                elif rle_type != 1:
                    rle = unpack('<h', f.read(2))[0]
                else:
                    rle = unpack('<B', f.read(1))[0]

                self.map[x].append(tile)


class Tile():
    """
    Object representing a single Tile in Terraria
    """

    def __init__(self):
        """
        Initializes the Tile Object
        :return:
        """

        self.active = False
        self.tile_type = None
        self.u = None
        self.v = None
        self.color = None
        self.wall = None
        self.wall_color = None
        self.liquid_type = None
        self.liquid_amount = None
        self.wire_red = False
        self.wire_blue = False
        self.wire_green = False
        self.brick_style = 0
        self.actuator = False
        self.actuator_inactive = False

    def clone(self):
        """
        Returns a copy of self tile object.
        :return: tile
        :return type: Tile
        """

        tile = Tile()

        tile.active = self.active
        tile.tile_type = self.tile_type
        tile.u = self.u
        tile.v = self.v
        tile.color = self.color
        tile.wall = self.wall
        tile.wall_color = self.wall_color
        tile.liquid_type = self.liquid_type
        tile.liquid_amount = self.liquid_amount
        tile.wire_red = self.wire_red
        tile.wire_blue = self.wire_blue
        tile.wire_green = self.wire_green
        tile.brick_style = self.brick_style
        tile.actuator = self.actuator
        tile.actuator_inactive = self.actuator_inactive

        return tile


class Chests():
    """
    Object representing the Chest Section of the World Object/File
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """
        self.total_chests = None
        self.max_items = None
        self.chests = []

    def load_chests(self, f, index):
        """
        Load chests from file (f) starting at (index)
        :param f:
        :param index:
        :return:
        """

        f.seek(index)

        self.total_chests = unpack('<h', f.read(2))[0]
        self.max_items = unpack('<h', f.read(2))[0]

        for i in range(0, self.total_chests):
            chest = Chest()

            chest.x = unpack('<i', f.read(4))[0]
            chest.y = unpack('<i', f.read(4))[0]
            chest.name = get_pstring(f)

            for j in range(0, self.max_items):
                chest.items.append([])

                stack_size = unpack('<h', f.read(2))[0]
                item_id = None
                item_prefix = None

                if stack_size > 0:
                    item_id = unpack('<i', f.read(4))[0]
                    item_prefix = unpack('<B', f.read(1))[0]

                chest.items[j] = [stack_size, item_id, item_prefix]

            self.chests.append(chest)


class Chest():
    """
    Object representing a Chest in the World Object
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """

        self.x = None
        self.y = None
        self.name = ''
        self.items = []