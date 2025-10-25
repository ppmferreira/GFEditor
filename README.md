# GF Editor � Vis�o geral inicial

Este reposit�rio cont�m um prot�tipo de GF Editor � uma aplica��o desktop escrita em Python com objetivo de ser modular, expans�vel e f�cil de empacotar como um .exe.

Objetivos principais
- Editor de dados do jogo (arquivos em `Lib/`) com suporte a diferentes encodings (Big5 para dados, ANSI para tradu��es).
- Arquitetura modular para permitir adi��o de parsers, validadores e plugins sem alterar o n�cleo.
- Ferramentas para desenvolvimento local e empacotamento (PyInstaller).

# GF Editor � Prot�tipo

Este reposit�rio cont�m um prot�tipo do GF Editor � uma aplica��o desktop em Python (PySide6) para editar arquivos do jogo organizados em campos delimitados por pipe (|).

Resumo r�pido
- C�digo principal em `src/` (GUI e utilit�rios de IO).
- M�dulos funcionais em `src/modules/` (cada m�dulo pode expor um painel via `panel_widget(parent)`).
- Assets do jogo ficam em `Assets/` (�cones, tradu��es, Client/Server INIs).

Requisitos
- Python 3.10+ (recomendado)
- Depend�ncias em `requirements.txt` (PySide6, Pillow, ...)

Como rodar (Windows, PowerShell)
1) Criar e ativar virtualenv:
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
2) Instalar depend�ncias:
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
- `src/gui.py` � Janela principal (lista de m�dulos � esquerda, painel direito para cada m�dulo).
- `src/gfio.py` � Leitura/grava��o de arquivos pipe-delimited com detec��o de encoding.
- `src/style/style.qss` � folha de estilo global (QSS) aplicada � aplica��o.
- `src/modules/*` � m�dulos (ex.: `items`) que prov�m UI e utilit�rios.
- `Assets/` � dados do jogo (Client, Server, Translate, itemicon, etc.).

Tradu��es (Assets/Translate)
- As tradu��es seguem formato `ID|Nome|Descri��o|` com suporte a descri��es multilinha (linhas seguintes pertencem � descri��o).
- O editor adiciona novas tradu��es no �ndice do item quando solicitado e preserva o formato com tr�s campos (ID, Nome, Descri��o).

Exemplo r�pido de m�dulo
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
- Veja `docs/contributing.md` e `docs/` para arquitetura, roadmap e guidelines de contribui��o.

Notas finais
- Fa�a backup de `Assets/Lib` antes de salvar altera��es.
- Este � um prot�tipo: mudan�as na UI/fluxo podem ocorrer.

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
- Veja `docs/contributing.md` para instru��es de desenvolvimento, testes e estilo.

## Licen�a & notas
- Este � um prot�tipo. Fa�a backups de `Lib/` antes de salvar qualquer altera��o.
