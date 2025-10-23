## Arquitetura (vis�o r�pida)

- Camada de IO: `src/gfio.py` � leitura/grava��o de arquivos pipe-delimited com detec��o de encoding.
- Camada de modelo: classes simples que representam linhas/registros (a definir conforme parser espec�fico).
- Camada de apresenta��o: `src/gui.py` (PySide6) � tabela edit�vel, busca, valida��o b�sica.
- Extensibilidade: pasta `src/plugins/` (plugin discovery) para adicionar novos parsers, validadores e ferramentas.

Princ�pios:
- M�dulos pequenos e test�veis
- Interfaces simples: read(path)->model, model->write(path)
- Backups autom�ticos antes de sobrescrever
