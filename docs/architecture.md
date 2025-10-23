## Arquitetura (visão rápida)

- Camada de IO: `src/gfio.py` — leitura/gravação de arquivos pipe-delimited com detecção de encoding.
- Camada de modelo: classes simples que representam linhas/registros (a definir conforme parser específico).
- Camada de apresentação: `src/gui.py` (PySide6) — tabela editável, busca, validação básica.
- Extensibilidade: pasta `src/plugins/` (plugin discovery) para adicionar novos parsers, validadores e ferramentas.

Princípios:
- Módulos pequenos e testáveis
- Interfaces simples: read(path)->model, model->write(path)
- Backups automáticos antes de sobrescrever
