from pathlib import Path
import sys
# ensure src package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from src.modules.items.translate import TranslateFile
import tempfile
p = Path(tempfile.gettempdir()) / 'test_T_pipe.tmp'
# create a file that simulates the problematic content (ASCII-only for test)
p.write_text('# header\n65444|Nucleo de Vitalidade do Leao Astral|$12$Duracao 24 horas|\n$12$O efeito nao pode ser acumulado com outros efeitos \n$12$identicos ou de mesma qualidade, Este item nao sera \n$12$consumido e podera ser reutilizado apos o tempo de recarga.||\n', encoding='utf-8')
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
