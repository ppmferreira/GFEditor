import csv
from typing import List, Tuple, Optional
from .model import Item

# Default header (based on documentation). Each comma in the docs is a pipe
DEFAULT_HEADER = [
    'Id', 'IconFilename', 'ModelId', 'ModelFilename', 'WeaponEffectId', 'FlyEffectId',
    'UsedEffectId', 'UsedSoundName', 'EnhanceEffectId', 'Name', 'ItemType', 'EquipType',
    'OpFlags', 'OpFlagsPlus', 'Target', 'RestrictGender', 'RestrictLevel', 'RestrictMaxLevel',
    'RebirthCount', 'RebirthScore', 'RebirthMaxScore', 'RestrictAlign', 'RestrictPrestige',
    'RestrictClass', 'ItemQuality', 'ItemGroup', 'CastingTime', 'CoolDownTime', 'CoolDownGroup',
    'MaxHp', 'MaxMp', 'Str', 'Vit', 'Int', 'Von', 'Agi', 'AvgPhysicoDamage', 'RandPhysicoDamage',
    'AttackRange', 'AttackSpeed', 'Attack', 'RangeAttack', 'PhysicoDefence', 'MagicDamage',
    'MagicDefence', 'HitRate', 'DodgeRate', 'PhysicoCriticalRate', 'PhysicoCriticalDamage',
    'MagicCriticalRate', 'MagicCriticalDamage', 'PhysicalPenetration', 'MagicalPenetration',
    'PhysicalPenetrationDefence', 'MagicalPenetrationDefence', 'Attribute', 'AttributeRate',
    'AttributeDamage', 'AttributeResist', 'SpecialType', 'SpecialRate', 'SpecialDamage', 'DropRate',
    'DropIndex', 'TreasureBuffs1', 'TreasureBuffs2', 'TreasureBuffs3', 'TreasureBuffs4', 'EnchantType',
    'EnchantId', 'ExpertLevel', 'ExpertEnchantId', 'ElfSkillId', 'EnchantTimeType', 'EnchantDuration',
    'LimitType', 'DueDateTime', 'BackpackSize', 'MaxSocket', 'SocketRate', 'MaxDurability',
    'MaxStack', 'ShopPriceType', 'SysPrice', 'RestrictEventPosId', 'MissionPosId', 'BlockRate',
    'LogLevel', 'AuctionType', 'ExtraData1', 'ExtraData2', 'ExtraData3', 'Tip'
]


def read_items(path: str, delimiter: str = '|', encoding: str = 'big5') -> Tuple[List[str], List[List[str]], List[Item]]:
    """Read a delimited file and return (header, rows, items).

    Notes:
    - Item data files (C_Item / S_Item) commonly use BIG5 encoding. This
      function defaults to `encoding='big5'` for compatibility.
    - header: list of column names
    - rows: list of lists of strings (original values)
    - items: list of `Item` instances built from the rows
    """
    header = []
    rows: List[List[str]] = []
    items: List[Item] = []

    # Try multiple encodings until we can successfully read the header.
    tried_encodings = [encoding, 'utf-8', 'latin-1']
    header = None
    rows_buffer: List[List[str]] = []
    used_encoding: Optional[str] = None

    for enc in tried_encodings:
        try:
            with open(path, 'r', encoding=enc, newline='') as ftemp:
                temp_reader = csv.reader(ftemp, delimiter=delimiter)
                try:
                    header = next(temp_reader)
                except StopIteration:
                    header = []
                    rows_buffer = []
                    used_encoding = enc
                    break
                rows_buffer = list(temp_reader)
                used_encoding = enc
                break
        except UnicodeDecodeError:
            # try next encoding
            continue

    if header is None:
        # Could not decode with tried encodings; attempt with the requested
        # encoding to raise the original error.
        with open(path, 'r', encoding=encoding, newline='') as ftemp:
            temp_reader = csv.reader(ftemp, delimiter=delimiter)
            try:
                header = next(temp_reader)
            except StopIteration:
                return [], [], []
            rows_buffer = list(temp_reader)

    # Enforce expected number of columns. The project uses a fixed
    # 93-column layout (DEFAULT_HEADER). If the detected header length
    # doesn't match, prefer DEFAULT_HEADER and treat the first line as
    # data when it looks numeric (Id in first column).
    expected_len = len(DEFAULT_HEADER)
    first_row: Optional[List[str]] = None
    if header is None:
        header = DEFAULT_HEADER.copy()
    elif len(header) != expected_len:
        # if header looks like data (starts with numeric id), use default
        if header and header[0] and header[0].lstrip('-').isdigit():
            first_row = header
            header = DEFAULT_HEADER.copy()
        else:
            # header present but wrong length: warn and fall back to default
            import warnings
            warnings.warn(f"Header length {len(header)} != expected {expected_len}; using DEFAULT_HEADER")
            header = DEFAULT_HEADER.copy()

    # If we detected the first row as data, process it first
    def normalize_row(r: List[str]) -> List[str]:
        if len(r) < expected_len:
            return r + [''] * (expected_len - len(r))
        if len(r) > expected_len:
            return r[:expected_len]
        return r

    if first_row is not None:
        row = normalize_row(first_row)
        rows.append(row)
        items.append(Item.from_row(header, row))

    # process buffered rows
    for row in rows_buffer:
        row = normalize_row(row)
        rows.append(row)
        items.append(Item.from_row(header, row))

    return header, rows, items


def read_items_pair(client_path: str, server_path: str, delimiter: str = '|', encoding: str = 'big5'):
    """Read client and server item files and ensure they contain the same data.

    Returns (header, rows, items). Raises ValueError if headers/rows differ.
    """
    h1, r1, items1 = read_items(client_path, delimiter=delimiter, encoding=encoding)
    h2, r2, items2 = read_items(server_path, delimiter=delimiter, encoding=encoding)

    if h1 != h2:
        raise ValueError(f"Headers differ between client ({client_path}) and server ({server_path})")
    if r1 != r2:
        raise ValueError(f"Row data differ between client ({client_path}) and server ({server_path})")

    return h1, r1, items1
