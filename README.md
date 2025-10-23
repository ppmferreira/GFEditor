# GF Editor — Visão geral inicial

Este repositório contém um protótipo de GF Editor — uma aplicação desktop escrita em Python com objetivo de ser modular, expansível e fácil de empacotar como um .exe.

Objetivos principais
- Editor de dados do jogo (arquivos em `Lib/`) com suporte a diferentes encodings (Big5 para dados, ANSI para traduções).
- Arquitetura modular para permitir adição de parsers, validadores e plugins sem alterar o núcleo.
- Ferramentas para desenvolvimento local e empacotamento (PyInstaller).

Estrutura do projeto (resumo relevante)
- `src/` — código-fonte principal (módulos importáveis diretamente). Contém:
  - `cli.py` — utilitário CLI (pequeno runner de linha de comando)
  - `gfio.py` — utilitários de leitura/gravação de arquivos pipe-delimited (detecção de encoding)
  - `gui.py` — GUI minimal implementada com PySide6 (protótipo)
  - `__init__.py`, `style/` — metadados e estilos
  - `modules/` — módulos funcionais organizados como pacotes (ex.: `src/modules/items/`). Cada módulo expõe uma função `panel_widget(parent)` para fornecer o painel da GUI e funções utilitárias como `list_entries(lib_path)`.
- `launch_gfeditor.py` / `launch_gfeditor_gui.py` — launchers que adicionam `src/` ao `sys.path` e iniciam o app
- `run_gfeditor.ps1` — helper PowerShell para criar/ativar venv e rodar a aplicação no Windows
- `build_exe.ps1` — helper para empacotar com PyInstaller (gera `dist\GFEditor.exe`)
- `Lib/` — dados do jogo (não modifique sem backup)
- `docs/` — documentação técnica (arquitetura, plugins, contribuição, roadmap)

Como rodar (rápido)
1) Criar e ativar um virtualenv na raiz (Windows PowerShell):
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
2) Instalar dependências:
```powershell
pip install -r requirements.txt
```
3) Rodar GUI (launcher adiciona `src` ao path):
```powershell
python launch_gfeditor_gui.py
```
ou usar o helper:
```powershell
.\run_gfeditor.ps1
```

Como empacotar um exe (Windows)
1) Certifique-se que `Lib/` está na raiz e que o venv tem as dependências instaladas.
2) Rode:
```powershell
.\build_exe.ps1
```
Depois coloque a pasta `Lib` ao lado do `.exe` em `dist\GFEditor\`.

Design modular e pontos de extensão
- O núcleo expõe funções de IO em `src/gfio.py`. Parsers/transformações devem ser implementados como módulos separados com interface simples (read -> model -> write).
- Plugins podem ser colocados em `src/plugins/` e descobertos por nome (convencionar um `entrypoint` simples).
- Documentação sobre plugins e API está em `docs/plugins.md`.

Como criar um novo módulo
- Crie uma pasta em `src/modules/<nome>/` e adicione um `__init__.py`.
- Exponha pelo menos:
  - `def panel_widget(parent) -> QWidget`: retorna o widget que será mostrado no painel direito.
  - `def list_entries(lib_path: pathlib.Path) -> list[str]`: opcional, retorna itens ou arquivos gerenciados pelo módulo.
- Exemplo mínimo (`src/modules/example/__init__.py`):

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from pathlib import Path

def list_entries(lib_path: Path):
    return []

def panel_widget(parent):
    w = QWidget(parent)
    l = QVBoxLayout()
    l.addWidget(QLabel('Example module'))
    w.setLayout(l)
    return w
```

Contribuindo
- Veja `docs/contributing.md` para instruções de desenvolvimento, testes e estilo.

Licença & notas
- Este é um protótipo. Faça backups de `Lib/` antes de salvar qualquer alteração.
