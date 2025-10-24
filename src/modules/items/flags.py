"""Item Flags and Enumerations for Grand Fantasia."""

# Item Flags (bit flags)
FLAGS = {
    'CanUse': 1,
    'NoDecrease': 2,
    'NoTrade': 4,
    'NoDiscard': 8,
    'OnlyStartBit': 16,
    'NoEnhance': 16,
    'ReplaceableStartBit': 21,
    'NoRepair': 32,
    'Combineable': 64,
    'BindOnEquip': 128,
    'AccumTime': 256,
    'NoSameBuff': 512,
    'NoInBattle': 1024,
    'NoInTown': 2048,
    'NoInCave': 4096,
    'NoInInstance': 8192,
    'LinkToQuest': 16384,
    'ForDead': 32768,
    'Only1': 65536,
    'Only2': 131072,
    'Only3': 262144,
    'Only4': 524288,
    'Only5': 1048576,
    'Only': 2031616,
    'Replaceable1': 2097152,
    'Replaceable2': 4194304,
    'Replaceable3': 8388608,
    'Replaceable4': 16777216,
    'Replaceable5': 33554432,
    'Replaceable': 65011712,
    'NoInBattlefield': 67108864,
    'NoInField': 134217728,
    'NoTransNode': 268435456,
    'UnBindItem': 536870912,
}

# OP FlagPlus (bit flags)
FLAGS_PLUS = {
    'IKCombine': 1,
    'GKCombine': 2,
    'EquipShow': 4,
    'PurpleWLimit': 8,
    'PurpleALimit': 16,
    'UseBind': 32,
    'OneStack': 64,
    'RideCombineIK': 128,
    'RideCombineGK': 256,
    'ISRideCombine': 384,
    'VIP': 512,
    'ChairCombineIK': 2048,
    'ChairCombineGK': 4096,
    'ISChairCombine': 6144,
    'RedWLimit': 8192,
    'RedALimit': 16384,
    'CrystalCombo': 32768,
    'SouvenirCombo': 65536,
    'GodAreaCombo': 131072,
    'ElftabletEquip': 262144,
    'ElftabletExp': 524288,
    'ShowProbability': 1048576,
    'StorageForbidden': 2097152,
    'FamilyStorageForbidden': 4194304,
}

# Item Quality
QUALITY = {
    1: 'Gray',
    2: 'Green',
    3: 'Blue',
    4: 'Orange',
    5: 'Yellow',
    6: 'Purple',
    7: 'Red',
    8: 'End',
}

QUALITY_REV = {v: k for k, v in QUALITY.items()}

# Item Target
TARGET = {
    1: 'None',
    2: 'ToSelf',
    3: 'ToElf',
    4: 'ToChar',
    5: 'ToItem',
    6: 'ToCrop',
    7: 'ToFarm',
    8: 'ToIsleScene',
    9: 'ToIsleStatue',
    10: 'ToHiredFarm',
    11: 'ToFishGround',
    12: 'ToFish',
    13: 'ToPit',
    14: 'ToMineral',
    15: 'ToPlant',
    16: 'ToIsleFarm',
    17: 'ToCattle',
    18: 'ToPasturage',
    19: 'ToESShortcut',
    20: 'ToMonster',
    21: 'ToNPC',
    22: 'ToSpellAA',
}

TARGET_REV = {v: k for k, v in TARGET.items()}

# Item Type
ITEM_TYPE = {
    0: 'Unknown',
    1: 'Head',
    2: 'Chest',
    3: 'Pants',
    4: 'Glove',
    5: 'Feet',
    6: 'Back',
    7: 'Sword',
    8: 'Claymore',
    9: 'Mace',
    10: 'WarHammer',
    11: 'Axe',
    12: 'BattleAxe',
    13: 'Bow',
    14: 'Gun',
    15: 'HolyItem',
    16: 'Staff',
    17: 'Shield',
    18: 'Trinket',
    19: 'Arrow',
    20: 'Bullet',
    21: 'Backpack',
    22: 'Item',
    23: 'Material',
    24: 'Rune',
    25: 'Scroll',
    26: 'SpellStone',
    27: 'EquipSet',
    28: 'Treasure',
    29: 'LuckyBag',
    30: 'ElfStone',
    31: 'ElfEquip',
    32: 'Chip',
    33: 'Formula',
    34: 'Crystal',
    35: 'Kuso',
    36: 'KusoOneHand',
    37: 'KusoTwoHand',
    38: 'KusoStaff',
    39: 'KusoBow',
    40: 'KusoGun',
    41: 'KusoShield',
    42: 'KusoSuit',
    43: 'ElfGameItem',
    44: 'WitchCraft',
    45: 'Building',
    46: 'UnBindItem',
    47: 'ElfBackpack',
    48: 'Food',
    49: 'MatchItem',
    50: 'KusoTrinket',
    51: 'ElfBook1',
    52: 'ElfBook2',
    53: 'ElfBook3',
    54: 'Machine',
    55: 'HeavyMachine',
    56: 'Cannon',
    57: 'Artillery',
    58: 'KusoSoulCrystal',
    59: 'CrystalKatana',
    60: 'CrystalKey',
    61: 'PostCard',
    62: 'Souvenir',
    63: 'OptionalLuckyBag',
    8001: 'CombineRate',
    8002: 'StrengthenRate',
    8003: 'CookRate',
    8004: 'MatchRate',
    8005: 'StrengthenTransfer',
    8006: 'RideCombinePoint',
    9001: 'OpenUIStart',
    9999: 'OpenUIEnd',
    10000: 'Max',
}

ITEM_TYPE_REV = {v: k for k, v in ITEM_TYPE.items()}


def decode_flags(value: int) -> list:
    """Decode integer flags into list of flag names."""
    flags = []
    for name, flag_value in FLAGS.items():
        if value & flag_value == flag_value and flag_value not in [16, 21]:  # Skip duplicates
            flags.append(name)
    return flags


def decode_flags_plus(value: int) -> list:
    """Decode integer FlagPlus into list of flag names."""
    flags = []
    for name, flag_value in FLAGS_PLUS.items():
        if value & flag_value == flag_value and flag_value not in [384, 6144]:  # Skip sum values
            flags.append(name)
    return flags


def encode_flags(flag_names: list) -> int:
    """Encode list of flag names into integer."""
    value = 0
    for name in flag_names:
        if name in FLAGS:
            value |= FLAGS[name]
    return value


def encode_flags_plus(flag_names: list) -> int:
    """Encode list of FlagPlus names into integer."""
    value = 0
    for name in flag_names:
        if name in FLAGS_PLUS:
            value |= FLAGS_PLUS[name]
    return value


def get_quality_name(value: int) -> str:
    """Get quality name from value."""
    return QUALITY.get(value, 'Unknown')


def get_quality_value(name: str) -> int:
    """Get quality value from name."""
    return QUALITY_REV.get(name, 1)


def get_target_name(value: int) -> str:
    """Get target name from value."""
    return TARGET.get(value, 'Unknown')


def get_target_value(name: str) -> int:
    """Get target value from name."""
    return TARGET_REV.get(name, 1)


def get_item_type_name(value: int) -> str:
    """Get item type name from value."""
    return ITEM_TYPE.get(value, 'Unknown')


def get_item_type_value(name: str) -> int:
    """Get item type value from name."""
    return ITEM_TYPE_REV.get(name, 0)
