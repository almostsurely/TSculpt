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


def store_pstring(string):
    """
    Returns (string) into a pascal string bytes.
    :param string:
    :return:
    """

    length_byte = pack('<B', len(string))

    chars = [c.encode() for c in string]
    string_bytes = pack('s' * len(chars), *chars)

    return length_byte + string_bytes


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
        self.signs = Signs()
        self.npcs = NPCs()
        self.footer = Footer()

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
        self.map.load_tile_importance(self.tile_importance)

        if f.tell() != self.section_pointers[2]:
            raise WorldFormatException('Chest location off from section pointer.')

        self.chests.load_chests(f, self.section_pointers[2])

        if f.tell() != self.section_pointers[3]:
            raise WorldFormatException('Sign location off from section pointer.')

        self.signs.load_signs(f, self.section_pointers[3])

        if f.tell() != self.section_pointers[4]:
            raise WorldFormatException('NPC location off from section pointer')

        self.npcs.load_npcs(f, self.section_pointers[4])

        if f.tell() != self.section_pointers[5]:
            raise WorldFormatException('Footer location off from section pointer.')

        self.footer.load_footer(f, self.section_pointers[5])

    def validate(self):
        """
        Returns if the world is valid and ready for saving.
        :return:
        """
        if self.version is None:
            return False
        if self.section_count is None:
            return False
        if len(self.section_pointers) == 0:
            return False
        if self.tile_type_count is None:
            return False
        if len(self.tile_importance) == 0:
            return False
        if not self.header.validate():
            return False
        if not self.map.validate():
            return False
        if not self.chests.validate():
            return False
        if not self.signs.validate():
            return False
        if not self.npcs.validate():
            return False
        if not self.footer.validate():
            return False

        return True

    def save_world(self, file):
        """
        Saves the World File
        :return:
        """
        version_bytes = pack('<i', 102)
        section_count_bytes = pack('<h', 10)
        tile_type_count_bytes = pack('<h', 340)

        mask = 0x01
        byte = 0
        byte_list = []
        for tile in self.tile_importance:
            if tile:
                byte |= mask

            if mask == 0x80:
                byte_list.append(pack('<B', byte))
                mask = 0x01
                byte = 0
                continue
            mask <<= 1

        byte_list.append(pack('<B', byte))

        tile_imprt_bytes = b''.join(byte_list)

        header_bytes = self.header.generate_bytestring()
        map_bytes = self.map.generate_bytestring()
        chest_bytes = self.chests.generate_bytestring()
        sign_bytes = self.signs.generate_bytestring()
        npc_bytes = self.npcs.generate_bytestring()
        footer_bytes = self.footer.generate_bytestring()

        pointer = len(version_bytes)
        pointer += len(section_count_bytes)
        pointer += len(tile_type_count_bytes)
        pointer += len(tile_imprt_bytes)
        pointer += 40

        pointers = []
        pointers.append(pointer)
        pointer += len(header_bytes)
        pointers.append(pointer)
        pointer += len(map_bytes)
        pointers.append(pointer)
        pointer += len(chest_bytes)
        pointers.append(pointer)
        pointer += len(sign_bytes)
        pointers.append(pointer)
        pointer += len(npc_bytes)
        pointers.append(pointer)
        pointers.append(0)
        pointers.append(0)
        pointers.append(0)
        pointers.append(0)

        pointer_bytes = b''
        for p in pointers:
            pointer_bytes += pack('<i', p)

        file.write(version_bytes)
        file.write(section_count_bytes)
        file.write(pointer_bytes)
        file.write(tile_type_count_bytes)
        file.write(tile_imprt_bytes)
        file.write(header_bytes)
        file.write(map_bytes)
        file.write(chest_bytes)
        file.write(sign_bytes)
        file.write(npc_bytes)
        file.write(footer_bytes)


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
        self.tree_x = ()
        self.tree_style = ()
        self.cave_back_x = ()
        self.cave_back_style = ()
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

    def validate(self):
        """
        Validates that the Header is accurate.
        :return:
        """

        if self.world_id is None:
            return False
        if self.x is None:
            return False
        if self.w is None:
            return False
        if self.y is None:
            return False
        if self.h is None:
            return False
        if self.y_tiles is None:
            return False
        if self.x_tiles is None:
            return False
        if self.moon_type is None:
            return False
        if len(self.tree_x) == 0:
            return False
        if len(self.tree_style) == 0:
            return False
        if len(self.cave_back_x) == 0:
            return False
        if len(self.cave_back_style) == 0:
            return False
        if self.ice_back_style is None:
            return False
        if self.jungle_back_style is None:
            return False
        if self.hell_back_style is None:
            return False
        if self.spawn_x is None:
            return False
        if self.spawn_y is None:
            return False
        if self.surface_level is None:
            return False
        if self.rock_layer is None:
            return False
        if self.temp_time is None:
            return False
        if self.is_day is None:
            return False
        if self.moon_phase is None:
            return False
        if self.is_blood_moon is None:
            return False
        if self.is_eclipse is None:
            return False
        if self.dungeon_x is None:
            return False
        if self.dungeon_y is None:
            return False
        if self.is_crimson is None:
            return False
        if self.is_boss_1_dead is None:
            return False
        if self.is_boss_2_dead is None:
            return False
        if self.is_boss_3_dead is None:
            return False
        if self.is_queen_bee_dead is None:
            return False
        if self.is_mech_1_dead is None:
            return False
        if self.is_mech_2_dead is None:
            return False
        if self.is_mech_3_dead is None:
            return False
        if self.is_any_mech_dead is None:
            return False
        if self.is_plant_dead is None:
            return False
        if self.is_golem_dead is None:
            return False
        if self.is_goblin_saved is None:
            return False
        if self.is_wizard_saved is None:
            return False
        if self.is_mechanic_saved is None:
            return False
        if self.is_goblins_beat is None:
            return False
        if self.is_clown_beat is None:
            return False
        if self.is_frost_beat is None:
            return False
        if self.is_pirates_beat is None:
            return False
        if self.is_orb_smashed is None:
            return False
        if self.is_meteor_spawned is None:
            return False
        if self.orb_smash_count is None:
            return False
        if self.altar_count is None:
            return False
        if self.is_hard_mode is None:
            return False
        if self.invasion_delay is None:
            return False
        if self.invasion_size is None:
            return False
        if self.invasion_type is None:
            return False
        if self.invasion_x is None:
            return False
        if self.is_temp_raining is None:
            return False
        if self.temp_rain_time is None:
            return False
        if self.temp_max_rain is None:
            return False
        if self.ore_tier_1 is None:
            return False
        if self.ore_tier_2 is None:
            return False
        if self.ore_tier_3 is None:
            return False
        if self.bg_tree is None:
            return False
        if self.bg_corruption is None:
            return False
        if self.bg_jungle is None:
            return False
        if self.bg_snow is None:
            return False
        if self.bg_hallow is None:
            return False
        if self.bg_crimson is None:
            return False
        if self.bg_desert is None:
            return False
        if self.bg_ocean is None:
            return False
        if self.cloud_bg_active is None:
            return False
        if self.num_clouds is None:
            return False
        if self.wind_speed_set is None:
            return False
        if self.num_anglers is None:
            return False
        if self.is_angler_saved is None:
            return False
        if self.angler_quest is None:
            return False

        return True

    def generate_bytestring(self):
        """
        Generates a bytestring to eventually save.
        :return:
        """
        bstring = b''

        bstring += store_pstring(self.world_name)
        bstring += pack('<i', self.world_id)
        bstring += pack('<i', self.x)
        bstring += pack('<i', self.w)
        bstring += pack('<i', self.y)
        bstring += pack('<i', self.h)
        bstring += pack('<i', self.y_tiles)
        bstring += pack('<i', self.x_tiles)
        bstring += pack('<B', self.moon_type)
        bstring += pack('<iii', *self.tree_x)
        bstring += pack('<iiii', *self.tree_style)
        bstring += pack('<iii', *self.cave_back_x)
        bstring += pack('<iiii', *self.cave_back_style)
        bstring += pack('<i', self.ice_back_style)
        bstring += pack('<i', self.jungle_back_style)
        bstring += pack('<i', self.hell_back_style)
        bstring += pack('<i', self.spawn_x)
        bstring += pack('<i', self.spawn_y)
        bstring += pack('<d', self.surface_level)
        bstring += pack('<d', self.rock_layer)
        bstring += pack('<d', self.temp_time)
        bstring += pack('<?', self.is_day)
        bstring += pack('<i', self.moon_phase)
        bstring += pack('<?', self.is_blood_moon)
        bstring += pack('<?', self.is_eclipse)
        bstring += pack('<i', self.dungeon_x)
        bstring += pack('<i', self.dungeon_y)
        bstring += pack('<?', self.is_crimson)
        bstring += pack('<?', self.is_boss_1_dead)
        bstring += pack('<?', self.is_boss_2_dead)
        bstring += pack('<?', self.is_boss_3_dead)
        bstring += pack('<?', self.is_queen_bee_dead)
        bstring += pack('<?', self.is_mech_1_dead)
        bstring += pack('<?', self.is_mech_2_dead)
        bstring += pack('<?', self.is_mech_3_dead)
        bstring += pack('<?', self.is_any_mech_dead)
        bstring += pack('<?', self.is_plant_dead)
        bstring += pack('<?', self.is_golem_dead)
        bstring += pack('<?', self.is_goblin_saved)
        bstring += pack('<?', self.is_wizard_saved)
        bstring += pack('<?', self.is_mechanic_saved)
        bstring += pack('<?', self.is_goblins_beat)
        bstring += pack('<?', self.is_clown_beat)
        bstring += pack('<?', self.is_frost_beat)
        bstring += pack('<?', self.is_pirates_beat)
        bstring += pack('<?', self.is_orb_smashed)
        bstring += pack('<?', self.is_meteor_spawned)
        bstring += pack('<B', self.orb_smash_count)
        bstring += pack('<i', self.altar_count)
        bstring += pack('<?', self.is_hard_mode)
        bstring += pack('<i', self.invasion_delay)
        bstring += pack('<i', self.invasion_size)
        bstring += pack('<i', self.invasion_type)
        bstring += pack('<d', self.invasion_x)
        bstring += pack('<?', self.is_temp_raining)
        bstring += pack('<i', self.temp_rain_time)
        bstring += pack('<f', self.temp_max_rain)
        bstring += pack('<i', self.ore_tier_1)
        bstring += pack('<i', self.ore_tier_2)
        bstring += pack('<i', self.ore_tier_3)
        bstring += pack('<B', self.bg_tree)
        bstring += pack('<B', self.bg_corruption)
        bstring += pack('<B', self.bg_jungle)
        bstring += pack('<B', self.bg_snow)
        bstring += pack('<B', self.bg_hallow)
        bstring += pack('<B', self.bg_crimson)
        bstring += pack('<B', self.bg_desert)
        bstring += pack('<B', self.bg_ocean)
        bstring += pack('<i', self.cloud_bg_active)
        bstring += pack('<h', self.num_clouds)
        bstring += pack('<f', self.wind_speed_set)
        bstring += pack('<i', self.num_anglers)
        bstring += pack('<?', self.is_angler_saved)
        bstring += pack('<i', self.angler_quest)

        return bstring


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
        self.tile_importance = None

    def load_tile_importance(self, tile_importance):
        self.tile_importance = tile_importance

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
                    tile.active = True

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

                if header_2 > 0:
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

    def validate(self):
        """
        Validates that the Map is good and ready to save
        :return:
        """

        if self.x_tiles == 0:
            return False
        if self.y_tiles == 0:
            return False
        if len(self.map) == 0:
            return False
        if len(self.map) != self.x_tiles:
            return False
        for x in range(0, self.x_tiles):
            if len(self.map[x]) != self.y_tiles:
                return False
            for y in range(0, self.y_tiles):
                if not self.map[x][y].validate():
                    return False
                pass

        return True

    def generate_bytestring(self):
        """
        Generate a bytestring for eventual saving.
        :return:
        """

        blist = []

        prev_tile = None
        rle = 0

        for x in range(0, self.x_tiles):
            for y in range(0, self.y_tiles):

                tile = self.map[x][y]

                if prev_tile is None:
                    prev_tile = tile
                    rle = 0
                elif tile == prev_tile:
                    rle += 1
                else:
                    blist.append([prev_tile.generate_bytestring(rle, self.tile_importance), prev_tile.tile_type, rle])
                    rle = 0
                    prev_tile = tile

            if prev_tile is not None:
                blist.append([prev_tile.generate_bytestring(rle, self.tile_importance), prev_tile.tile_type, rle])
                prev_tile = None
                rle = 0

        bstring = b''.join(b[0] for b in blist)

        return bstring


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
        self.u = -1
        self.v = -1
        self.color = None
        self.wall = None
        self.wall_color = None
        self.liquid_type = 0
        self.liquid_amount = None
        self.wire_red = False
        self.wire_blue = False
        self.wire_green = False
        self.brick_style = 0
        self.actuator = False
        self.actuator_inactive = False

    def __eq__(self, other):
        """
        Tests if two Tiles are equal to one another.
        :param other:
        :return:
        """

        if isinstance(other, Tile):
            return (
                self.active == other.active and
                self.tile_type == other.tile_type and
                self.u == other.u and
                self.v == other.v and
                self.color == other.color and
                self.wall == other.wall and
                self.wall_color == other.wall_color and
                self.liquid_type == other.liquid_type and
                self.liquid_amount == other.liquid_amount and
                self.wire_red == other.wire_red and
                self.wire_blue == other.wire_blue and
                self.wire_green == other.wire_green and
                self.brick_style == other.brick_style and
                self.actuator == other.actuator and
                self.actuator_inactive == other.actuator_inactive
            )
        else:
            return NotImplemented

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

    def validate(self):
        """
        Validates the Tile
        :return:
        """
        if self.active is False:
            return True
        else:
            if self.tile_type is None:
                return False

        return True

    def generate_bytestring(self, rle, tile_importance):
        """
        Generate a byte array for the tile to eventually save.
        :return:
        """

        bstring = b''

        header_1 = 0
        header_2 = 0
        header_3 = 0

        if rle == 0:
            pass
        elif rle > 255:
            header_1 |= 128
        else:
            header_1 |= 64

        if self.active:
            header_1 |= 2

        if self.wall is not None:
            header_1 |= 4

        if self.tile_type is not None and self.tile_type > 255:
            header_1 |= 32

        if self.wire_red:
            header_2 |= 2
        if self.wire_green:
            header_2 |= 4
        if self.wire_blue:
            header_2 |= 8

        if self.brick_style != 0:
            header_2 |= (self.brick_style << 4)

        if self.actuator:
            header_3 |= 2
        if self.actuator_inactive:
            header_3 |= 4
        if self.color is not None:
            header_3 |= 8
        if self.wall_color is not None:
            header_3 |= 16

        if header_3 > 0:
            header_2 |= 1
        if header_2 > 0:
            header_1 |= 1

        header_1 |= self.liquid_type

        bstring += pack('<B', header_1)
        if header_1 & 1 == 1:
            bstring += pack('<B', header_2)
        if header_2 & 1 == 1:
            bstring += pack('<B', header_3)

        if self.tile_type is not None:
            if self.tile_type < 255:
                bstring += pack('<B', self.tile_type)
            else:
                bstring += pack('<h', self.tile_type)

            if tile_importance[self.tile_type]:
                bstring += pack('<h', self.u)
                bstring += pack('<h', self.v)

        if self.color is not None:
            bstring += pack('<B', self.color)

        if self.wall is not None:
            bstring += pack('<B', self.wall)

        if self.wall_color is not None:
            bstring += pack('<B', self.wall_color)

        if self.liquid_amount is not None and self.liquid_amount > 0:
            bstring += pack('<B', self.liquid_amount)

        if rle > 255:
            bstring += pack('<h', rle)
        elif rle > 0:
            bstring += pack('<B', rle)

        return bstring


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

    def validate(self):
        """
        Validates all the chests
        :return:
        """

        if self.max_items is None:
            return False

        for chest in self.chests:
            if not chest.validate():
                return False

        return True

    def generate_bytestring(self):
        """
        Generates a Bytestring to eventually save.
        :return:
        """

        bstring = b''

        bstring += pack('<h', self.total_chests)
        bstring += pack('<h', self.max_items)

        for chest in self.chests:
            bstring += pack('<i', chest.x)
            bstring += pack('<i', chest.y)
            string = store_pstring(chest.name)
            bstring += string

            for item in chest.items:
                bstring += pack('<h', item[0])
                if item[0] > 0:
                    bstring += pack('<i', item[1])
                    bstring += pack('<B', item[2])

        return bstring


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

    def validate(self):
        """
        Validates the chest
        :return:
        """
        if self.x is None:
            return False
        if self.y is None:
            return False
        if len(self.items) == 0:
            return False
        for item in self.items:
            if item[0] > 0:
                if not item[1]:
                    return False
                if not item[2]:
                    return False

        return True


class Signs():
    """
    Object representing the Signs section in the World Object
    """

    def __init__(self):
        """
        Initializes the Object.
        :return:
        """

        self.total_signs = 0
        self.signs = []

    def load_signs(self, f, index):
        """
        Loads signs from file (f) starting at (index)
        :param f:
        :param index:
        :return:
        """

        f.seek(index)

        self.total_signs = unpack('<h', f.read(2))[0]

        for i in range(0, self.total_signs):
            sign = Sign()

            sign.text = get_pstring(f)
            sign.x = unpack('<i', f.read(4))[0]
            sign.y = unpack('<i', f.read(4))[0]

            self.signs.append(sign)

    def validate(self):
        """
        Validates that all signs are valid
        :return:
        """

        for sign in self.signs:
            if not sign.validate():
                return False

        return True

    def generate_bytestring(self):
        """
        Generates a bytestring for eventually saving.
        :return:
        """

        bstring = b''

        bstring += pack('<h', self.total_signs)

        for sign in self.signs:
            bstring += store_pstring(sign.text)
            bstring += pack('<i', sign.x)
            bstring += pack('<i', sign.y)

        return bstring


class Sign():
    """
    Object representing a Sign in Terraria
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """

        self.text = ''
        self.x = None
        self.y = None

    def validate(self):
        """
        Validates the Sign
        :return: valid
        """

        if self.text == '':
            return False

        if self.x is None:
            return False

        if self.y is None:
            return False

        return True


class NPCs():
    """
    Object representing the NPCs Section of the World Object/File
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """

        self.npcs = []

    def load_npcs(self, f, index):
        """
        Load the NPCs from file (f) starting at (index)
        :param f:
        :param index:
        :return:
        """

        f.seek(index)

        while unpack('<?', f.read(1))[0]:
            npc = NPC()

            npc.name = get_pstring(f)
            npc.display_name = get_pstring(f)
            npc.x = unpack('<f', f.read(4))[0]
            npc.y = unpack('<f', f.read(4))[0]
            npc.is_homeless = unpack('<?', f.read(1))[0]
            npc.home_x = unpack('<i', f.read(4))[0]
            npc.home_y = unpack('<i', f.read(4))[0]

            self.npcs.append(npc)

    def validate(self):
        """
        Validates the NPC Section
        :return : valid
        """

        for npc in self.npcs:
            if not npc.validate():
                return False

        return True

    def generate_bytestring(self):
        """
        Generate a bytestring for eventual storage.
        :return:
        """

        bytestring = b''

        for npc in self.npcs:
            bytestring += pack('<?', True)
            bytestring += store_pstring(npc.name)
            bytestring += store_pstring(npc.display_name)
            bytestring += pack('<f', npc.x)
            bytestring += pack('<f', npc.y)
            bytestring += pack('<?', npc.is_homeless)
            bytestring += pack('<i', npc.home_x)
            bytestring += pack('<i', npc.home_y)

        bytestring += pack('<?', False)

        return bytestring


class NPC():
    """
    Object representing an NPC in Terraria
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """

        self.name = ''
        self.display_name = ''
        self.x = None
        self.y = None
        self.is_homeless = True
        self.home_x = None
        self.home_y = None

    def validate(self):
        """
        Validates that this is an accurate NPC
        :return:
        """

        if self.name == '':
            return False

        if self.display_name == '':
            return False

        if self.x is None:
            return False

        if self.y is None:
            return False

        if self.home_x is None:
            return False

        if self.home_y is None:
            return False

        return True


class Footer():
    """
    Object representing the Footer of the World File
    """

    def __init__(self):
        """
        Initializes the Object
        :return:
        """

        self.valid = False
        self.title = ''
        self.world_id = None

    def load_footer(self, f, index):
        """
        Loads the footer from file (f) starting at (index)
        :param f:
        :param index:
        :return:
        """

        f.seek(index)

        self.valid = unpack('<?', f.read(1))[0]
        self.title = get_pstring(f)
        self.world_id = unpack('<i', f.read(4))[0]

    def validate(self):
        """
        Validates the Footer object as complete and ready to save.
        :return:
        """

        if not self.valid:
            return False

        if self.title == '':
            return False

        if not self.world_id:
            return False

        return True

    def generate_bytestring(self):
        """
        Generate a bytestring for saving eventually
        :return:
        """

        bstring = b''

        bstring += pack('<?', self.valid)
        bstring += store_pstring(self.title)
        bstring += pack('<i', self.world_id)

        return bstring