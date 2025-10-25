# GF Editor — Visão geral inicial

Este repositório contém um protótipo de GF Editor — uma aplicação desktop escrita em Python com objetivo de ser modular, expansível e fácil de empacotar como um .exe.

Objetivos principais
- Editor de dados do jogo (arquivos em `Lib/`) com suporte a diferentes encodings (Big5 para dados, ANSI para traduções).
- Arquitetura modular para permitir adição de parsers, validadores e plugins sem alterar o núcleo.
- Ferramentas para desenvolvimento local e empacotamento (PyInstaller).

# GF Editor — Protótipo

Este repositório contém um protótipo do GF Editor — uma aplicação desktop em Python (PySide6) para editar arquivos do jogo organizados em campos delimitados por pipe (|).

Resumo rápido
- Código principal em `src/` (GUI e utilitários de IO).
- Módulos funcionais em `src/modules/` (cada módulo pode expor um painel via `panel_widget(parent)`).
- Assets do jogo ficam em `Assets/` (ícones, traduções, Client/Server INIs).

Requisitos
- Python 3.10+ (recomendado)
- Dependências em `requirements.txt` (PySide6, Pillow, ...)

Como rodar (Windows, PowerShell)
1) Criar e ativar virtualenv:
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
2) Instalar dependências:
```powershell
pip install -r requirements.txt
```
3) Rodar a GUI:
```powershell
python launch_gfeditor_gui.py
```
ou usar o helper:
```powershell
.\run_gfeditor.ps1
```

Estrutura relevante
- `src/gui.py` — Janela principal (lista de módulos à esquerda, painel direito para cada módulo).
- `src/gfio.py` — Leitura/gravação de arquivos pipe-delimited com detecção de encoding.
- `src/style/style.qss` — folha de estilo global (QSS) aplicada à aplicação.
- `src/modules/*` — módulos (ex.: `items`) que provêm UI e utilitários.
- `Assets/` — dados do jogo (Client, Server, Translate, itemicon, etc.).

Traduções (Assets/Translate)
- As traduções seguem formato `ID|Nome|Descrição|` com suporte a descrições multilinha (linhas seguintes pertencem à descrição).
- O editor adiciona novas traduções no índice do item quando solicitado e preserva o formato com três campos (ID, Nome, Descrição).

Exemplo rápido de módulo
Crie `src/modules/example/__init__.py` com:
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

Empacotar como .exe (Windows)
- Ver `build_exe.ps1` para o fluxo com PyInstaller. Lembre-se de incluir a pasta `Lib/` ao lado do `.exe` quando distribuir.

Contribuindo
- Veja `docs/contributing.md` e `docs/` para arquitetura, roadmap e guidelines de contribuição.

Notas finais
- Faça backup de `Assets/Lib` antes de salvar alterações.
- Este é um protótipo: mudanças na UI/fluxo podem ocorrer.

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

## Contribuindo
- Veja `docs/contributing.md` para instruções de desenvolvimento, testes e estilo.

## Licença & notas
- Este é um protótipo. Faça backups de `Lib/` antes de salvar qualquer alteração.
