import traceback
try:
    import modules.items
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    raise
