import sys, traceback
sys.path.insert(0, r'e:/GFEDITOR/src')
try:
    import modules.items
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    raise
