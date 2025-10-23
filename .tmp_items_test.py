import os
import csv
from src.modules.items.reader import read_items
from src.modules.items.writer import write_items_pair


def main():
    sample_path = os.path.join('Lib', 'data', 'S_Item_test.txt')
    os.makedirs(os.path.dirname(sample_path), exist_ok=True)

    header = [
        "Id",
        "IconFilename",
        "ModelId",
        "ModelFilename",
        "Name",
        "ItemType",
        "SysPrice",
        "MaxStack",
        "Tip",
    ]

    rows = [
        ["1001", "A00001.dds", "200", "model_200.mdl", "Test Sword", "Weapon", "1500", "1", "Uma espada de teste"],
        ["1002", "A00002.dds", "201", "model_201.mdl", "Test Potion", "Consumable", "50", "99", "Poção de teste"],
    ]

    with open(sample_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='|')
        w.writerow(header)
        for r in rows:
            w.writerow(r)

    h, rws, items = read_items(sample_path)
    print('Read header:', h)
    print('Rows:', len(rws))
    print('Items:', len(items))

    client_out = os.path.join('Lib', 'data', 'db', 'C_Item_test.txt')
    server_out = os.path.join('Lib', 'data', 'serverdb', 'S_Item_test_out.txt')
    write_items_pair(h, rws, client_out, server_out)
    print('Wrote to:', client_out, server_out)
    print('First item object:', items[0])


if __name__ == '__main__':
    main()
