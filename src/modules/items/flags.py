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


# Class list for RestrictClass bitmask (order matters for bit positions)
# Canonical classes and their server IDs (provided by user). Order below
# determines the bit position used by RestrictClass mask in the editor UI.
CLASSES = [
    # Guerreiras (Warrior-like)
    'Lutador','Guerreiro','Berzerker','Paladino','Titan','Templario','Cavaleiro da Morte','Cavaleiro Real','Destruidor','Cavaleiro Sagrado',
    # Arqueiras (Archer-like)
    'Cacador','Arqueiro','Ranger','Assassin','Franco Atirador','Sicario Sombrio','Mercenario','Ninja','Predador','Shinobi',
    # Sacerdotes (Priest-like)
    'Acolito','Sacerdote','Clerigo','Sabio','Profeta','Mistico','Mensageiro Divino','Xama','Arcanjo','Druida',
    # Magicas (Magic)
    'Bruxo','Mago','Feiticeiro','Necromante','Arquimago','Demonologo','Arcano','Emissario dos Mortos','Shinigami',
    # Maquinista (Machinist)
    'Maquinista Aprendiz','Maquinista','Agressor','Demolidor','Prime','Optimus','Megatron','Galvatron','Omega','Titan Celeste',
    # Viajante (Traveler)
    'Viajante','Nomade','Espadachim','Ilusionista','Samurai','Augure','Ronin','Oraculo','Mestre Dimensional','Cronos'
]

# Map from class name -> server ID (as provided)
CLASS_IDS = {
    # Guerreiras
    'Lutador': 1,
    'Guerreiro': 2,
    'Berzerker': 3,
    'Paladino': 4,
    'Titan': 17,
    'Templario': 18,
    'Cavaleiro da Morte': 32,
    'Cavaleiro Real': 33,
    'Destruidor': 40,
    'Cavaleiro Sagrado': 41,
    # Arqueiras
    'Cacador': 5,
    'Arqueiro': 6,
    'Ranger': 7,
    'Assassin': 8,
    'Franco Atirador': 19,
    'Sicario Sombrio': 20,
    'Mercenario': 34,
    'Ninja': 35,
    'Predador': 42,
    'Shinobi': 43,
    # Sacerdotes
    'Acolito': 9,
    'Sacerdote': 10,
    'Clerigo': 11,
    'Sabio': 12,
    'Profeta': 21,
    'Mistico': 22,
    'Mensageiro Divino': 36,
    'Xama': 37,
    'Arcanjo': 44,
    'Druida': 45,
    # Mágicas
    'Bruxo': 13,
    'Mago': 14,
    'Feiticeiro': 15,
    'Necromante': 16,
    'Arquimago': 23,
    'Demonologo': 24,
    'Arcano': 38,
    'Emissario dos Mortos': 39,
    'Shinigami': 47,
    # Maquinista
    'Maquinista Aprendiz': 25,
    'Maquinista': 26,
    'Agressor': 27,
    'Demolidor': 28,
    'Prime': 29,
    'Optimus': 30,
    'Megatron': 48,
    'Galvatron': 49,
    'Omega': 50,
    'Titan Celeste': 51,
    # Viajante
    'Viajante': 52,
    'Nomade': 53,
    'Espadachim': 54,
    'Ilusionista': 55,
    'Samurai': 56,
    'Augure': 57,
    'Ronin': 58,
    'Oraculo': 59,
    'Mestre Dimensional': 60,
    'Cronos': 61,
}

# reverse map id -> name (useful for looking up server-side class names)
ID_TO_CLASS = {v: k for k, v in CLASS_IDS.items()}


def decode_restrict_class(mask: int) -> list:
    """Decode RestrictClass bitmask into list of class names (according to CLASSES order).

    The mask is interpreted such that bit i corresponds to CLASSES[i].
    """
    out = []
    for i, cname in enumerate(CLASSES):
        if mask & (1 << i):
            out.append(cname)
    return out


def encode_restrict_class(class_names: list) -> int:
    """Encode a list of class names into a RestrictClass bitmask using CLASSES order."""
    mask = 0
    for cname in class_names:
        try:
            idx = CLASSES.index(cname)
            mask |= (1 << idx)
        except ValueError:
            # ignore unknown class names
            pass
    return mask


def get_class_id(name: str) -> int:
    return CLASS_IDS.get(name)


def get_class_name(idv: int) -> str:
    return ID_TO_CLASS.get(idv)


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


def ids_to_hex(ids) -> str:
    """Convert an iterable of bit positions (0..127) into a compact hex string.

    Mirrors the C++ example provided: sets bit i for each id in ids and
    returns the hex digits (lowercase) without leading zeros. Returns '0'
    when no bits are set.
    """
    n = 0
    for i in ids:
        try:
            ii = int(i)
        except Exception:
            continue
        if 0 <= ii < 128:
            n |= (1 << ii)
    if n == 0:
        return '0'
    return format(n, 'x')


def hex_to_ids(hexstr: str):
    """Convert a hex mask (string) back to a sorted list of bit positions set.

    Accepts strings with or without 0x prefix. Returns list[int].
    """
    if not hexstr:
        return []
    s = str(hexstr).strip().lower()
    if s.startswith('0x'):
        s = s[2:]
    try:
        n = int(s, 16)
    except Exception:
        return []
    out = []
    pos = 0
    while n:
        if n & 1:
            out.append(pos)
        n >>= 1
        pos += 1
    return out


def class_names_to_hex(class_names) -> str:
    """Given an iterable of class names (as used in `CLASS_IDS`),
    produce a hex mask where the server class ID numbers are used as bit positions.

    Example: class_names_to_hex(['SomeClass']) -> hex where bit at CLASS_IDS['SomeClass'] is set.
    """
    ids = []
    for cname in class_names:
        cid = CLASS_IDS.get(cname)
        if cid is not None:
            ids.append(cid)
    return ids_to_hex(ids)


def class_names_to_mask(class_names) -> int:
    """Return integer mask using server-class-ID positions for given class names."""
    n = 0
    for cname in class_names:
        cid = CLASS_IDS.get(cname)
        if cid is None:
            # try if cname is numeric string
            try:
                cid = int(cname)
            except Exception:
                cid = None
        if cid is not None and 0 <= cid < 128:
            n |= (1 << cid)
    return n
