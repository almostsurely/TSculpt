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