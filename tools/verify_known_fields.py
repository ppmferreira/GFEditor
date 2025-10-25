"""Verify known_fields in panel.py

Produces a summary of fields declared in known_fields and compares with
fields used in other blocks (basic, parameters, enchant, advanced, restrictions).
Output: list of missing fields and duplicate literals (if any).
"""

import re
from pathlib import Path

PANEL = Path(r'e:/GFEDITOR/src/modules/items/panel.py')
# read with ignore errors to handle non-utf8 bytes in the file
text = PANEL.read_text(encoding='utf-8', errors='ignore')

def extract_keys_between(label):
    m = re.search(rf"{re.escape(label)}\s*=\s*\{{(.*?)\}}", text, re.S)
    if not m:
        return []
    body = m.group(1)
    keys = re.findall(r"[\'\"]([A-Za-z0-9_]+)[\'\"]\s*:\s*", body)
    return keys

# extract known_fields (literal set)
m = re.search(r"known_fields\s*=\s*\{(.*?)\}\s*", text, re.S)
known_list = []
if m:
    known_body = m.group(1)
    known_list = re.findall(r"[\'\"]([A-Za-z0-9_]+)[\'\"]", known_body)

# other blocks that define fields
basic_keys = extract_keys_between('fields_basic')
params_keys = extract_keys_between('params')
enchant_keys = extract_keys_between('enchant_fields')
advanced_keys = extract_keys_between('advanced_fields')

# restrictions dict (in function) - look for restrict_fields
m2 = re.search(r"restrict_fields\s*=\s*\{(.*?)\}\s*", text, re.S)
restrict_keys = []
if m2:
    restrict_keys = re.findall(r"[\'\"]([A-Za-z0-9_]+)[\'\"]\s*:\s*", m2.group(1))

explicit_keys = set(['OpFlags','OpFlagsPlus','RestrictClass','Tip','IconFilename','Id','Name','ItemType','ItemQuality','Target'])

other_fields = set(basic_keys) | set(params_keys) | set(enchant_keys) | set(advanced_keys) | set(restrict_keys) | explicit_keys
known_set = set(known_list)

missing = sorted(list(other_fields - known_set))
duplicates = sorted([k for k in known_list if known_list.count(k) > 1])

print('=== known_fields summary for src/modules/items/panel.py ===')
print(f'Known fields (count {len(known_list)}):')
print(', '.join(sorted(known_set)))
print('\nFields used in other tabs (count {}):'.format(len(other_fields)))
print(', '.join(sorted(other_fields)))
print('\nFields MISSING from known_fields (should be added so Raw tab does not duplicate):')
if missing:
    for k in missing:
        print(' -', k)
else:
    print(' (none)')

print('\nDuplicate literals inside known_fields (if any):')
if duplicates:
    for k in set(duplicates):
        print(' -', k)
else:
    print(' (none)')

if missing:
    print('\nSuggested addition to known_fields (append these names):')
    print(', '.join([f"'{k}'" for k in missing]))

