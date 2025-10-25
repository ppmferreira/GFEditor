import sys
sys.path.insert(0, r'e:/GFEDITOR/src')
from modules.items import flags as f
s='20200040014'
dec=int(s)
hexv=int(s,16)
print('dec:',dec, 'hexv:',hex(hexv))
dec_matches=[f.ID_TO_CLASS.get(b) for b in range(128) if dec & (1<<b) and f.ID_TO_CLASS.get(b)]
hex_matches=[f.ID_TO_CLASS.get(b) for b in range(128) if hexv & (1<<b) and f.ID_TO_CLASS.get(b)]
print('dec_matches',dec_matches)
print('hex_matches',hex_matches)
print('choose hex?' , len(hex_matches) > len(dec_matches) and len(hex_matches)>0)
PY