from pathlib import Path
import sys
sys.path.insert(0, 'src')
from modules import items, monsters, npcs, shops
p = Path.cwd() / 'Lib'
print('Lib exists:', p.exists())
print('items.sample:', items.list_entries(p)[:5])
print('monsters.sample:', monsters.list_entries(p)[:5])
print('npcs.sample:', npcs.list_entries(p)[:5])
print('shops.sample:', shops.list_entries(p)[:5])
