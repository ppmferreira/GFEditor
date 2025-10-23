# -*- coding: cp1252 -*-
from pathlib import Path

# Complete SCHEMA for Item columns (indices 0..92) provided by the user.
# Types: 'int', 'str', 'trans' (translation key for Name), 'trans_multiline' (Tip),
# 'enum:<n>' and 'flags:<n>' for special handling in UI.
SCHEMA = [
    (0, 'Id', 'int'),
    (1, 'IconFilename', 'str'),
    (2, 'ModelId', 'int'),
    (3, 'ModelFilename', 'str'),
    (4, 'WeaponEffectId', 'int'),
    (5, 'FlyEffectId', 'int'),
    (6, 'UsedEffectId', 'int'),
    (7, 'UsedSoundName', 'str'),
    (8, 'EnhanceEffectId', 'int'),
    (9, 'Name', 'trans'),
    (10, 'ItemType', 'enum:ItemType'),
    (11, 'EquipType', 'int'),
    (12, 'OpFlags', 'flags:OpFlags'),
    (13, 'OpFlagsPlus', 'flags:OpFlagsPlus'),
    (14, 'Target', 'enum:Target'),
    (15, 'RestrictGender', 'int'),
    (16, 'RestrictLevel', 'int'),
    (17, 'RestrictMaxLevel', 'int'),
    (18, 'RebirthCount', 'int'),
    (19, 'RebirthScore', 'int'),
    (20, 'RebirthMaxScore', 'int'),
    (21, 'RestrictAlign', 'int'),
    (22, 'RestrictPrestige', 'int'),
    (23, 'RestrictClass', 'flags:RestrictClass'),
    (24, 'ItemQuality', 'enum:ItemQuality'),
    (25, 'ItemGroup', 'int'),
    (26, 'CastingTime', 'int'),
    (27, 'CoolDownTime', 'int'),
    (28, 'CoolDownGroup', 'int'),
    (29, 'MaxHp', 'int'),
    (30, 'MaxMp', 'int'),
    (31, 'Str', 'int'),
    (32, 'Con', 'int'),
    (33, 'Int', 'int'),
    (34, 'Vol', 'int'),
    (35, 'Dex', 'int'),
    (36, 'AvgPhysicoDamage', 'int'),
    (37, 'RandPhysicoDamage', 'int'),
    (38, 'AttackRange', 'int'),
    (39, 'AttackSpeed', 'int'),
    (40, 'Attack', 'int'),
    (41, 'RangeAttack', 'int'),
    (42, 'PhysicoDefence', 'int'),
    (43, 'MagicDamage', 'int'),
    (44, 'MagicDefence', 'int'),
    (45, 'HitRate', 'int'),
    (46, 'DodgeRate', 'int'),
    (47, 'PhysicoCriticalRate', 'int'),
    (48, 'PhysicoCriticalDamage', 'int'),
    (49, 'MagicCriticalRate', 'int'),
    (50, 'MagicCriticalDamage', 'int'),
    (51, 'PhysicalPenetration', 'int'),
    (52, 'MagicalPenetration', 'int'),
    (53, 'PhysicalPenetrationDefence', 'int'),
    (54, 'MagicalPenetrationDefence', 'int'),
    (55, 'Attribute', 'int'),
    (56, 'AttributeRate', 'int'),
    (57, 'AttributeDamage', 'int'),
    (58, 'AttributeResist', 'int'),
    (59, 'SpecialType', 'int'),
    (60, 'SpecialRate', 'int'),
    (61, 'SpecialDamage', 'int'),
    (62, 'DropRate', 'int'),
    (63, 'DropIndex', 'int'),
    (64, 'TreasureBuffs_0', 'int'),
    (65, 'TreasureBuffs_1', 'int'),
    (66, 'TreasureBuffs_2', 'int'),
    (67, 'TreasureBuffs_3', 'int'),
    (68, 'EnchantType', 'int'),
    (69, 'EnchantId', 'int'),
    (70, 'ExpertLevel', 'int'),
    (71, 'ExpertEnchantId', 'int'),
    (72, 'ElfSkillId', 'int'),
    (73, 'EnchantTimeType', 'int'),
    (74, 'EnchantDuration', 'int'),
    (75, 'LimitType', 'int'),
    (76, 'DueDateTime', 'str'),
    (77, 'BackpackSize', 'int'),
    (78, 'MaxSocket', 'int'),
    (79, 'SocketRate', 'int'),
    (80, 'MaxDurability', 'int'),
    (81, 'MaxStack', 'int'),
    (82, 'ShopPriceType', 'int'),
    (83, 'SysPrice', 'int'),
    (84, 'RestrictEventPosId', 'int'),
    (85, 'MissionPosId', 'int'),
    (86, 'BlockRate', 'int'),
    (87, 'LogLevel', 'int'),
    (88, 'AuctionType', 'int'),
    (89, 'ExtraData_0', 'str'),
    (90, 'ExtraData_1', 'str'),
    (91, 'ExtraData_2', 'str'),
    (92, 'Tip', 'trans_multiline'),
]

# Enums and flags provided by the user
ENUMS = {
    'ItemType': {},
    'Target': {
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
    },
    'ItemQuality': {
        1: 'Gray',
        2: 'Green',
        3: 'Blue',
        4: 'Orange',
        5: 'Yellow',
        6: 'Purple',
        7: 'Red',
        8: 'End',
    },
}

# Fill ItemType mapping provided by the user
ENUMS['ItemType'] = {
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

# OpFlags (exact values provided)
OPFLAGS = {
    'CanUse': 1,
    'NoDecrease': 2,
    'NoTrade': 4,
    'NoDiscard': 8,
    'OnlyStartBit': 16,
    'NoEnhance': 16,  # note: duplicate value in original list
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

# OP FlagPlus (exact values provided)
OPFLAGSPLUS = {
    'IKCombine': 1,
    'GKCombine': 2,
    'EquipShow': 4,
    'PurpleWLimit': 8,
    'PurpleALimit': 16,
    'UseBind': 32,
    'OneStack': 64,
    'RideCombineIK': 128,
    'RideCombineGK': 256,
    'ISRideCombine': 384,  # 128 + 256
    'VIP': 512,
    'ChairCombineIK': 2048,
    'ChairCombineGK': 4096,
    'ISChairCombine': 6144,  # 2048 + 4096
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

# RestrictClass explicit mapping (ids provided by user)
ENUMS['RestrictClass'] = {
    # Classes Guerreiras
    1: 'Lutador',
    2: 'Guerreiro',
    3: 'Berzerker',
    4: 'Paladino',
    17: 'Titan',
    18: 'Templario',
    32: 'Cavaleiro da Morte',
    33: 'Cavaleiro Real',
    40: 'Destruidor',
    41: 'Cavaleiro Sagrado',

    # Classes Arqueiras
    5: 'Caçador',
    6: 'Arqueiro',
    7: 'Ranger',
    8: 'Assassin',
    19: 'Franco Atirador',
    20: 'Sicario Sombrio',
    34: 'Mercenario',
    35: 'Ninja',
    42: 'Predador',
    43: 'Shinobi',

    # Classes Sacerdotes
    9: 'Acolito',
    10: 'Sacerdote',
    11: 'Clerigo',
    12: 'Sabio',
    21: 'Profeta',
    22: 'Mistico',
    36: 'Mensageiro Divino',
    37: 'Xamã',
    44: 'Arcanjo',
    45: 'Druida',

    # Classes Mágicas
    13: 'Bruxo',
    14: 'Mago',
    15: 'Feiticeiro',
    16: 'Necromante',
    23: 'Arquimago',
    24: 'Demonologo',
    38: 'Arcano',
    39: 'Emissario dos Mortos',
    47: 'Shinigami',

    # Classes Maquinista
    25: 'Maquinista Aprendiz',
    26: 'Maquinista',
    27: 'Agressor',
    28: 'Demolidor',
    29: 'Prime',
    30: 'Optimus',
    48: 'Megatron',
    49: 'Galvatron',
    50: 'Omega',
    51: 'Titan Celeste',

    # Classes Viajante
    52: 'Viajante',
    53: 'Nomade',
    54: 'Espadachim',
    55: 'Ilusionista',
    56: 'Samurai',
    57: 'Augure',
    58: 'Ronin',
    59: 'Oraculo',
    60: 'Mestre Dimensional',
    61: 'Cronos',
}


# Helpers to convert between list of bit indices and hex bitmask
def ids_to_hex(ids):
    """Convert iterable of bit indices (0..127) to hex string (no leading 0x).
    Accepts ints. Example: ids_to_hex([61]) -> hex string with bit 61 set.
    """
    n = 0
    for i in ids:
        if not isinstance(i, int):
            raise TypeError("ids must be integers")
        if i < 0 or i >= 128:
            raise ValueError("bit index out of range (0..127): %r" % i)
        n |= (1 << i)
    return format(n, 'x') if n != 0 else "0"


def hex_to_ids(hexstr):
    """Convert hex string to list of set bit indices (ascending)."""
    if hexstr is None:
        return []
    s = hexstr.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    if s == "" or s == "0":
        return []
    n = int(s, 16)
    ids = []
    i = 0
    while n:
        if n & 1:
            ids.append(i)
        n >>= 1
        i += 1
    return ids

