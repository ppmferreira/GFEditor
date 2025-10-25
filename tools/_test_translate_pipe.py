from pathlib import Path
import sys
# ensure src package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from src.modules.items.translate import TranslateFile
import tempfile
p = Path(tempfile.gettempdir()) / 'test_T_pipe.tmp'
# create a file that simulates the problematic content
p.write_text('# header\n65444|Núcleo de Vitalidade do Leão Astral|$12$Duração 24 horas|\n$12$O efeito não pode ser acumulado com outros efeitos \n$12$idênticos ou de mesma qualidade, Este item não será \n$12$consumido e poderá ser reutilizado após o tempo de recarga.||\n', encoding='utf-8')
print('Before file:')
print(p.read_text(encoding='utf-8'))
# load
tf = TranslateFile(p)
print('\nLoaded records:')
print(tf.records)
# save to same path
tf.save()
print('\nAfter save:')
print(p.read_text(encoding='utf-8'))
