from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from src.modules.items.translate import TranslateFile
import tempfile
p = Path(tempfile.gettempdir()) / 'test_T_append.tmp'
if p.exists():
    p.unlink()
print('Using test file:', p)
# load (file does not exist)
tf = TranslateFile(p)
print('Initial records:', tf.records)
# set new translation -> should append
tf.set('99999', 'Nome Teste', 'Linha1\nLinha2')
tf.save()
print('After save content:\n')
print(p.read_text(encoding='utf-8'))
# add another new translation
from time import sleep
sleep(0.1)
tf2 = TranslateFile(p)
tf2.set('100000', 'Outro Nome', 'A\nB\nC')
tf2.save()
print('\nAfter second save content:\n')
print(p.read_text(encoding='utf-8'))
