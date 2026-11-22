from typing import Dict, List, NamedTuple

BASE_LOC_ID = 7_770_300  # AP location ID = BASE_LOC_ID + (owlevel - 1) * 4 + color_index

# color_index: 0=Grey, 1=Red, 2=Green, 3=Blue
COLOR_NAMES = ["Grey", "Red", "Green", "Blue"]

# wOWLevel order matches level_constants.asm const_def ordering.
# Each entry: (wOWLevel, level_name, compass_region)
LEVEL_LIST: List[tuple] = [
    # North (N1–N6)
    (1,  "Out of the Woods",       "North"),
    (2,  "The Peaceful Village",   "North"),
    (3,  "The Vast Plain",         "North"),
    (4,  "Bank of the Wild River", "North"),
    (5,  "The Tidal Coast",        "North"),
    (6,  "Sea Turtle Rocks",       "North"),
    # West (W1–W6)
    (7,  "Desert Ruins",           "West"),
    (8,  "The Volcano's Base",     "West"),
    (9,  "The Pool of Rain",       "West"),
    (10, "A Town in Chaos",        "West"),
    (11, "Beneath the Waves",      "West"),
    (12, "The West Crater",        "West"),
    # South (S1–S6)
    (13, "The Grasslands",         "South"),
    (14, "The Big Bridge",         "South"),
    (15, "Tower of Revival",       "South"),
    (16, "The Steep Canyon",       "South"),
    (17, "Cave of Flames",         "South"),
    (18, "Above the Clouds",       "South"),
    # East (E1–E7)
    (19, "The Stagnant Swamp",     "East"),
    (20, "The Frigid Sea",         "East"),
    (21, "Castle of Illusions",    "East"),
    (22, "The Colossal Hole",      "East"),
    (23, "The Warped Void",        "East"),
    (24, "The East Crater",        "East"),
    (25, "Forest of Fear",         "East"),
]


class WL3LocationData(NamedTuple):
    ap_id: int
    owlevel: int        # wOWLevel (1–25)
    color_index: int    # 0=Grey, 1=Red, 2=Green, 3=Blue
    region: str         # "North" / "West" / "South" / "East"
    level_name: str
    color_name: str

    @property
    def loc_index(self) -> int:
        """0-based index into the 100-entry chest table: (owlevel-1)*4 + color_index."""
        return (self.owlevel - 1) * 4 + self.color_index


def _build_location_table() -> Dict[str, WL3LocationData]:
    table: Dict[str, WL3LocationData] = {}
    for owlevel, level_name, region in LEVEL_LIST:
        for color_index, color_name in enumerate(COLOR_NAMES):
            loc_name = f"{level_name} - {color_name} Chest"
            ap_id = BASE_LOC_ID + (owlevel - 1) * 4 + color_index
            table[loc_name] = WL3LocationData(
                ap_id=ap_id,
                owlevel=owlevel,
                color_index=color_index,
                region=region,
                level_name=level_name,
                color_name=color_name,
            )
    return table


LOCATION_TABLE: Dict[str, WL3LocationData] = _build_location_table()

assert len(LOCATION_TABLE) == 100, f"Expected 100 locations, got {len(LOCATION_TABLE)}"

# Reverse lookup: ap_id → location name
ID_TO_LOCATION: Dict[int, str] = {loc.ap_id: name for name, loc in LOCATION_TABLE.items()}


# ---------------------------------------------------------------------------
# Key locations  (one per level × color; IDs 7_770_400 – 7_770_499)
# ---------------------------------------------------------------------------

KEY_BASE_LOC_ID = 7_770_400  # AP location ID = KEY_BASE_LOC_ID + (owlevel-1)*4 + color_index


class WL3KeyLocationData(NamedTuple):
    ap_id: int
    owlevel: int        # wOWLevel (1–25)
    color_index: int    # 0=Grey, 1=Red, 2=Green, 3=Blue
    region: str
    level_name: str
    color_name: str


def _build_key_location_table() -> Dict[str, WL3KeyLocationData]:
    table: Dict[str, WL3KeyLocationData] = {}
    for owlevel, level_name, region in LEVEL_LIST:
        for color_index, color_name in enumerate(COLOR_NAMES):
            loc_name = f"{level_name} - {color_name} Key"
            ap_id = KEY_BASE_LOC_ID + (owlevel - 1) * 4 + color_index
            table[loc_name] = WL3KeyLocationData(
                ap_id=ap_id,
                owlevel=owlevel,
                color_index=color_index,
                region=region,
                level_name=level_name,
                color_name=color_name,
            )
    return table


KEY_LOCATION_TABLE: Dict[str, WL3KeyLocationData] = _build_key_location_table()


# ---------------------------------------------------------------------------
# Coin locations (coinsanity)
# 200 musical coins (25 levels × 8 each); AP IDs 7_770_500 – 7_770_699.
# Spawn-order index 0-7 within the level (deterministic per level visit).
# ---------------------------------------------------------------------------

COIN_BASE_LOC_ID = 7_770_500
COINS_PER_LEVEL = 8


class WL3CoinLocationData(NamedTuple):
    ap_id: int
    owlevel: int        # wOWLevel (1–25)
    coin_index: int     # 0–7 (spawn order within the level)
    region: str
    level_name: str

    @property
    def loc_index(self) -> int:
        """0-based index into the 200-entry coin space: (owlevel-1)*8 + coin_index."""
        return (self.owlevel - 1) * COINS_PER_LEVEL + self.coin_index


def _build_coin_location_table() -> Dict[str, WL3CoinLocationData]:
    table: Dict[str, WL3CoinLocationData] = {}
    for owlevel, level_name, region in LEVEL_LIST:
        for coin_index in range(COINS_PER_LEVEL):
            loc_name = f"{level_name} - Big Coin {coin_index + 1}"
            ap_id = COIN_BASE_LOC_ID + (owlevel - 1) * COINS_PER_LEVEL + coin_index
            table[loc_name] = WL3CoinLocationData(
                ap_id=ap_id,
                owlevel=owlevel,
                coin_index=coin_index,
                region=region,
                level_name=level_name,
            )
    return table


COIN_LOCATION_TABLE: Dict[str, WL3CoinLocationData] = _build_coin_location_table()
assert len(COIN_LOCATION_TABLE) == 200, f"Expected 200 coin locations, got {len(COIN_LOCATION_TABLE)}"


# ---------------------------------------------------------------------------
# Boss defeat locations — one check per boss, fires when the boss dies.
# IDs 7_770_700 – 7_770_709. Boss order intentionally matches
# BOSS_CHEST_LOCATIONS in __init__.py so the boss_index below == index into
# wBossDefeatedFlags (ROM-side per-bit tracking).
# ---------------------------------------------------------------------------

BOSS_DEFEAT_BASE_LOC_ID = 7_770_700


class WL3BossDefeatLocationData(NamedTuple):
    ap_id: int
    boss_index: int      # 0-9, matches wBossDefeatedFlags bit index
    owlevel: int
    region: str
    level_name: str
    boss_name: str


# (boss_index, boss_name, owlevel) — owlevel/region come from LEVEL_LIST.
# Order MUST match wBossDefeatedFlags bit index in the ROM.
_BOSSES = [
    (0, "Wormwould",  13, "The Grasslands"),        # Grasslands boss
    (1, "Shoot",      10, "A Town in Chaos"),       # ATiC boss
    (2, "Scowler",     6, "Sea Turtle Rocks"),      # Sea Turtle Rocks boss
    (3, "Jamano",     19, "The Stagnant Swamp"),    # Stagnant Swamp (green chest boss)
    (4, "Anonster",    1, "Out of the Woods"),      # Out of the Woods boss
    (5, "Wolfenboss",  9, "The Pool of Rain"),      # Pool of Rain boss
    (6, "Pesce",       4, "Bank of the Wild River"),# BotWR boss
    (7, "Muddee",     19, "The Stagnant Swamp"),    # Stagnant Swamp (red chest boss)
    (8, "Doll Boy",    8, "The Volcano's Base"),    # Volcano's Base boss
    (9, "Yellow Belly", 7, "Desert Ruins"),         # Desert Ruins boss
]


def _build_boss_defeat_location_table() -> Dict[str, WL3BossDefeatLocationData]:
    table: Dict[str, WL3BossDefeatLocationData] = {}
    level_region = {name: region for _, name, region in LEVEL_LIST}
    for boss_index, boss_name, owlevel, level_name in _BOSSES:
        loc_name = f"{boss_name} - Defeated"
        table[loc_name] = WL3BossDefeatLocationData(
            ap_id=BOSS_DEFEAT_BASE_LOC_ID + boss_index,
            boss_index=boss_index,
            owlevel=owlevel,
            region=level_region[level_name],
            level_name=level_name,
            boss_name=boss_name,
        )
    return table


BOSS_DEFEAT_LOCATION_TABLE: Dict[str, WL3BossDefeatLocationData] = _build_boss_defeat_location_table()
assert len(BOSS_DEFEAT_LOCATION_TABLE) == 10, \
    f"Expected 10 boss defeat locations, got {len(BOSS_DEFEAT_LOCATION_TABLE)}"


# --------------------- Shopsanity ---------------------
# 10 shop AP locations. Player purchases each slot with in-game coins at the
# old-man shop NPC (new OW tile east of the hidden temple). ROM sets bit N
# in wShopSlotsBought on purchase; client detects the rising edge.
SHOP_BASE_LOC_ID = 7_770_800
NUM_SHOP_SLOTS = 10


class WL3ShopLocationData(NamedTuple):
    ap_id: int
    slot_index: int        # 0-9, matches wShopSlotsBought bit index
    region: str


def _build_shop_location_table() -> Dict[str, WL3ShopLocationData]:
    table: Dict[str, WL3ShopLocationData] = {}
    for slot_index in range(NUM_SHOP_SLOTS):
        loc_name = f"Shop Slot {slot_index + 1}"
        table[loc_name] = WL3ShopLocationData(
            ap_id=SHOP_BASE_LOC_ID + slot_index,
            slot_index=slot_index,
            # Grouped under NORTH region because the shop NPC tile lives on
            # the OW North map (east of the Hidden Temple). All OW compass
            # regions are unconditionally reachable, so this only affects
            # hint/spoiler grouping.
            region="North",
        )
    return table


SHOP_LOCATION_TABLE: Dict[str, WL3ShopLocationData] = _build_shop_location_table()
assert len(SHOP_LOCATION_TABLE) == NUM_SHOP_SLOTS, \
    f"Expected {NUM_SHOP_SLOTS} shop locations, got {len(SHOP_LOCATION_TABLE)}"


# --------------------- Coin Blocksanity ---------------------
# 44 locations — blocks that always drop a colour coin when broken (the
# same blocks "reveal hidden blocks and colour coins" highlights). Unlike
# COIN_BASE_LOC_ID's fixed 8-per-level, this count varies per level (0-5
# real entries; max 8 slots reserved on the ROM side). idx (0-7) is the
# SAME slot index wColourCoinBlockFlags uses — both this table and the
# ROM's ColourCoinBlockPositions come from one generator run
# (tools/build_colour_coin_block_table.py) so they can't drift apart.
# ROM still grants the normal +10 coins on pickup regardless of this
# option; the AP check just fires alongside it.
COIN_BLOCK_BASE_LOC_ID = 7_770_900
COIN_BLOCK_SLOTS_PER_LEVEL = 8


class WL3CoinBlockLocationData(NamedTuple):
    ap_id: int
    owlevel: int        # wOWLevel (1-25)
    block_index: int    # 0-7, matches wColourCoinBlockFlags bit index
    abs_x: int           # block-grid coords in the level's decompressed
    abs_y: int           # block map (not pixels) — see color_coin_positions.py
    region: str
    level_name: str

    @property
    def loc_index(self) -> int:
        """0-based index into the 200-slot space: (owlevel-1)*8 + block_index."""
        return (self.owlevel - 1) * COIN_BLOCK_SLOTS_PER_LEVEL + self.block_index


def _build_coin_block_location_table() -> Dict[str, WL3CoinBlockLocationData]:
    from .colour_coin_block_table import COLOUR_COIN_BLOCK_TABLE
    level_info = {owlevel: (name, region) for owlevel, name, region in LEVEL_LIST}
    table: Dict[str, WL3CoinBlockLocationData] = {}
    for owlevel, idx, abs_x, abs_y, _block_id in COLOUR_COIN_BLOCK_TABLE:
        level_name, region = level_info[owlevel]
        loc_name = f"{level_name} - Coin Block {idx + 1}"
        ap_id = COIN_BLOCK_BASE_LOC_ID + (owlevel - 1) * COIN_BLOCK_SLOTS_PER_LEVEL + idx
        table[loc_name] = WL3CoinBlockLocationData(
            ap_id=ap_id,
            owlevel=owlevel,
            block_index=idx,
            abs_x=abs_x,
            abs_y=abs_y,
            region=region,
            level_name=level_name,
        )
    return table


COIN_BLOCK_LOCATION_TABLE: Dict[str, WL3CoinBlockLocationData] = _build_coin_block_location_table()
assert len(COIN_BLOCK_LOCATION_TABLE) == 44, \
    f"Expected 44 coin block locations, got {len(COIN_BLOCK_LOCATION_TABLE)}"


# ---------------------------------------------------------------------------
# Door signposts — one check per locked door that has a signpost beside it
# (read_sign rows in DoorSigns, block_functions.asm). Reading it (Up at the
# sign) sets the door's bit in wDoorSignFlags. AP id = DOOR_SIGN_BASE_LOC_ID
# + door index (the ROM's DOOR_* constant), which is also the sign's slot in
# SignItems / TrapSignTable and its wDoorSignFlags bit.
# ---------------------------------------------------------------------------
DOOR_SIGN_BASE_LOC_ID = 7_771_100


class WL3DoorSignLocationData(NamedTuple):
    ap_id: int
    door_index: int     # DOOR_* constant (treasure_constants.asm)
    region: str
    level_name: str


# (door index, owlevel, door letter) — must match the ROM's read_sign rows.
_DOOR_SIGNS = [
    (0, 1, "A"),  # DOOR_N1_A
    (2, 1, "D"),  # DOOR_N1_D
    (3, 1, "B"),  # DOOR_N1_B
    (4, 2, "A"),  # DOOR_N2_A
    (5, 2, "B"),  # DOOR_N2_B
    (1, 2, "C"),  # DOOR_N2_C
    (6, 2, "E"),  # DOOR_N2_E
    (8, 2, "D"),  # DOOR_N2_D
    (7, 2, "F"),  # DOOR_N2_F
    (9, 3, "A"),  # DOOR_N3_A
    (10, 3, "B"),  # DOOR_N3_B
    (11, 4, "F"),  # DOOR_N4_F
    (12, 4, "G"),  # DOOR_N4_G
    (13, 4, "A"),  # DOOR_N4_A
    (14, 4, "B"),  # DOOR_N4_B
    (15, 4, "C"),  # DOOR_N4_C
    (16, 4, "D"),  # DOOR_N4_D
    (17, 4, "E"),  # DOOR_N4_E
    (18, 5, "A"),  # DOOR_N5_A
    (19, 5, "B"),  # DOOR_N5_B
    (20, 5, "C"),  # DOOR_N5_C
    (21, 5, "H"),  # DOOR_N5_H
    (22, 5, "F"),  # DOOR_N5_F
    (23, 5, "I"),  # DOOR_N5_I
    (24, 5, "D"),  # DOOR_N5_D (underwater)
    (25, 5, "E"),  # DOOR_N5_E (underwater)
    (26, 6, "B"),  # DOOR_N6_B (underwater)
    (27, 6, "C"),  # DOOR_N6_C (underwater, Scepter variants)
    (28, 6, "A"),  # DOOR_N6_A
    (29, 6, "D"),  # DOOR_N6_D (night-vision door while dark)
    (30, 7, "C"),  # DOOR_W1_C
    (31, 7, "D"),  # DOOR_W1_D
    (32, 7, "B"),  # DOOR_W1_B
    (33, 7, "A"),  # DOOR_W1_A
    (34, 7, "I"),  # DOOR_W1_I
    (35, 7, "F"),  # DOOR_W1_F
    (36, 7, "E"),  # DOOR_W1_E
    (37, 7, "H"),  # DOOR_W1_H
    (38, 7, "G"),  # DOOR_W1_G
    (39, 8, "E"),  # DOOR_W2_E
    (40, 8, "A"),  # DOOR_W2_A
    (41, 8, "C"),  # DOOR_W2_C
    (42, 8, "D"),  # DOOR_W2_D
    (43, 8, "G"),  # DOOR_W2_G
    (44, 8, "B"),  # DOOR_W2_B
    (45, 9, "C"),  # DOOR_W3_C
    (46, 9, "A"),  # DOOR_W3_A
    (47, 9, "E"),  # DOOR_W3_E
    (48, 10, "A"),  # DOOR_W4_A
    (49, 10, "B"),  # DOOR_W4_B
    (50, 10, "D"),  # DOOR_W4_D
    (51, 10, "G"),  # DOOR_W4_G
    (52, 10, "C"),  # DOOR_W4_C
    (53, 10, "J"),  # DOOR_W4_J
    (54, 10, "K"),  # DOOR_W4_K
    (55, 10, "L"),  # DOOR_W4_L
    (56, 10, "H"),  # DOOR_W4_H
    (57, 10, "I"),  # DOOR_W4_I
    (58, 11, "B"),  # DOOR_W5_B
    (59, 11, "A"),  # DOOR_W5_A
    (60, 11, "G"),  # DOOR_W5_G
    (61, 11, "F"),  # DOOR_W5_F
    (62, 11, "E"),  # DOOR_W5_E
    (63, 11, "D"),  # DOOR_W5_D
    (64, 11, "C"),  # DOOR_W5_C
    (65, 12, "B"),  # DOOR_W6_B
    (66, 12, "A"),  # DOOR_W6_A
    (67, 12, "C"),  # DOOR_W6_C
    (68, 13, "A"),  # DOOR_S1_A
    (69, 13, "B"),  # DOOR_S1_B
    (70, 13, "C"),  # DOOR_S1_C
    (71, 13, "D"),  # DOOR_S1_D
    (72, 13, "E"),  # DOOR_S1_E
    (73, 13, "G"),  # DOOR_S1_G
    (74, 13, "F"),  # DOOR_S1_F
    (75, 13, "I"),  # DOOR_S1_I
    (76, 13, "H"),  # DOOR_S1_H
    (77, 14, "E"),  # DOOR_S2_E
    (78, 14, "C"),  # DOOR_S2_C
    (79, 14, "D"),  # DOOR_S2_D
    (80, 14, "B"),  # DOOR_S2_B
    (81, 14, "A"),  # DOOR_S2_A
    (82, 15, "B"),  # DOOR_S3_B
    (83, 17, "A"),  # DOOR_S5_A
    (84, 17, "C"),  # DOOR_S5_C
    (85, 17, "D"),  # DOOR_S5_D
    (86, 17, "B"),  # DOOR_S5_B
    (87, 18, "A"),  # DOOR_S6_A
    (88, 18, "B"),  # DOOR_S6_B
    (89, 18, "F"),  # DOOR_S6_F
    (90, 18, "D"),  # DOOR_S6_D
    (91, 18, "C"),  # DOOR_S6_C
    (92, 19, "A"),  # DOOR_E1_A
    # 93: DOOR_E1_UNUSED_D dropped (always-open QoL door)
    (94, 19, "D"),  # DOOR_E1_D
    (95, 19, "B"),  # DOOR_E1_B
    (96, 20, "A"),  # DOOR_E2_A
    (97, 20, "C"),  # DOOR_E2_C
    (98, 20, "B"),  # DOOR_E2_B
    (99, 20, "D"),  # DOOR_E2_D
    (100, 20, "E"),  # DOOR_E2_E
    (101, 21, "A"),  # DOOR_E3_A
    (102, 21, "B"),  # DOOR_E3_B
    (103, 21, "C"),  # DOOR_E3_C
    (104, 21, "D"),  # DOOR_E3_D
    (105, 21, "G"),  # DOOR_E3_G
    (106, 21, "F"),  # DOOR_E3_F
    (107, 21, "E"),  # DOOR_E3_E
    (108, 22, "D"),  # DOOR_E4_D
    (109, 22, "C"),  # DOOR_E4_C
    (110, 22, "A"),  # DOOR_E4_A
    (111, 22, "B"),  # DOOR_E4_B
    (112, 24, "A"),  # DOOR_E6_A
    (113, 24, "C"),  # DOOR_E6_C
    (114, 24, "B"),  # DOOR_E6_B
    (115, 25, "C"),  # DOOR_E7_C
    (116, 25, "A"),  # DOOR_E7_A
    (117, 25, "B"),  # DOOR_E7_B
    # (118, 23, "A"),  # DOOR_E5_A  -- E5 doors off for now (2026-11-18): too many doors and locks for the logic
    # (119, 23, "O"),  # DOOR_E5_O
    # (120, 23, "D"),  # DOOR_E5_D
    # (121, 23, "N"),  # DOOR_E5_N
    # (122, 23, "C"),  # DOOR_E5_C
    # (123, 23, "F"),  # DOOR_E5_F
    # (124, 23, "B"),  # DOOR_E5_B
    # (125, 23, "K"),  # DOOR_E5_K
    # (126, 23, "L"),  # DOOR_E5_L
    # (127, 23, "M"),  # DOOR_E5_M
    # (128, 23, "J"),  # DOOR_E5_J
    # (129, 23, "I"),  # DOOR_E5_I
]


def _build_door_sign_location_table() -> Dict[str, WL3DoorSignLocationData]:
    level_info = {owlevel: (name, region) for owlevel, name, region in LEVEL_LIST}
    table: Dict[str, WL3DoorSignLocationData] = {}
    for door_index, owlevel, letter in _DOOR_SIGNS:
        level_name, region = level_info[owlevel]
        table[f"{level_name} - Door {letter} Sign"] = WL3DoorSignLocationData(
            ap_id=DOOR_SIGN_BASE_LOC_ID + door_index,
            door_index=door_index,
            region=region,
            level_name=level_name,
        )
    return table


DOOR_SIGN_LOCATION_TABLE: Dict[str, WL3DoorSignLocationData] = _build_door_sign_location_table()
