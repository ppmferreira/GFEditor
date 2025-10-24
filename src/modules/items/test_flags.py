"""Examples and tests for item flags decoding."""

from flags import (
    decode_flags, decode_flags_plus, encode_flags, encode_flags_plus,
    get_quality_name, get_item_type_name, get_target_name,
    FLAGS, FLAGS_PLUS, QUALITY, ITEM_TYPE, TARGET
)


def test_decode_flags():
    """Test flag decoding."""
    # Example: value with CanUse (1) and NoTrade (4) and BindOnEquip (128)
    test_value = 1 | 4 | 128  # = 133
    flags = decode_flags(test_value)
    print(f"Flags for {test_value}: {flags}")
    # Output: ['CanUse', 'NoTrade', 'BindOnEquip']


def test_decode_flags_plus():
    """Test FlagPlus decoding."""
    # Example: VIP (512) + IKCombine (1)
    test_value = 512 | 1  # = 513
    flags = decode_flags_plus(test_value)
    print(f"FlagPlus for {test_value}: {flags}")
    # Output: ['IKCombine', 'VIP']


def test_encode_flags():
    """Test flag encoding."""
    flags_list = ['CanUse', 'NoTrade', 'BindOnEquip']
    value = encode_flags(flags_list)
    print(f"Encoded flags {flags_list}: {value}")
    # Output: 133


def test_quality():
    """Test quality lookups."""
    for quality_value in [1, 2, 3, 4, 5, 6, 7]:
        name = get_quality_name(quality_value)
        print(f"Quality {quality_value}: {name}")


def test_item_type():
    """Test item type lookups."""
    for type_id in [1, 2, 3, 7, 8, 22, 23]:
        name = get_item_type_name(type_id)
        print(f"ItemType {type_id}: {name}")


def test_target():
    """Test target lookups."""
    for target_id in [1, 2, 3, 4, 5]:
        name = get_target_name(target_id)
        print(f"Target {target_id}: {name}")


def print_all_flags():
    """Print all available flags."""
    print("\n=== ALL FLAGS ===")
    for name, value in sorted(FLAGS.items(), key=lambda x: x[1]):
        print(f"{name}: {value}")


def print_all_flags_plus():
    """Print all available FlagPlus."""
    print("\n=== ALL FLAGS PLUS ===")
    for name, value in sorted(FLAGS_PLUS.items(), key=lambda x: x[1]):
        print(f"{name}: {value}")


if __name__ == '__main__':
    test_decode_flags()
    test_decode_flags_plus()
    test_encode_flags()
    test_quality()
    test_item_type()
    test_target()
    print_all_flags()
    print_all_flags_plus()
