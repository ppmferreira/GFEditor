# GF Editor � Vis�o geral inicial

Este reposit�rio cont�m um prot�tipo de GF Editor � uma aplica��o desktop escrita em Python com objetivo de ser modular, expans�vel e f�cil de empacotar como um .exe.

Objetivos principais
- Editor de dados do jogo (arquivos em `Lib/`) com suporte a diferentes encodings (Big5 para dados, ANSI para tradu��es).
- Arquitetura modular para permitir adi��o de parsers, validadores e plugins sem alterar o n�cleo.
- Ferramentas para desenvolvimento local e empacotamento (PyInstaller).

Estrutura do projeto (resumo relevante)
- `src/` � c�digo-fonte principal (m�dulos import�veis diretamente). Cont�m:
  - `cli.py` � utilit�rio CLI (pequeno runner de linha de comando)
  - `gfio.py` � utilit�rios de leitura/grava��o de arquivos pipe-delimited (detec��o de encoding)
  - `gui.py` � GUI minimal implementada com PySide6 (prot�tipo)
  - `__init__.py`, `style/` � metadados e estilos
  - `modules/` � m�dulos funcionais organizados como pacotes (ex.: `src/modules/items/`). Cada m�dulo exp�e uma fun��o `panel_widget(parent)` para fornecer o painel da GUI e fun��es utilit�rias como `list_entries(lib_path)`.
- `launch_gfeditor.py` / `launch_gfeditor_gui.py` � launchers que adicionam `src/` ao `sys.path` e iniciam o app
- `run_gfeditor.ps1` � helper PowerShell para criar/ativar venv e rodar a aplica��o no Windows
- `build_exe.ps1` � helper para empacotar com PyInstaller (gera `dist\GFEditor.exe`)
- `Lib/` � dados do jogo (n�o modifique sem backup)
- `docs/` � documenta��o t�cnica (arquitetura, plugins, contribui��o, roadmap)

Como rodar (r�pido)
1) Criar e ativar um virtualenv na raiz (Windows PowerShell):
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
2) Instalar depend�ncias:
```powershell
# GF Editor � Vis�o geral inicial

Este reposit�rio cont�m um prot�tipo de GF Editor � uma aplica��o desktop escrita em Python com objetivo de ser modular, expans�vel e f�cil de empacotar como um .exe.

## Objetivos principais
- Editor de dados do jogo (arquivos em `Lib/`) com suporte a diferentes encodings (Big5 para dados, ANSI para tradu��es).
- Arquitetura modular para permitir adi��o de parsers, validadores e plugins sem alterar o n�cleo.
- Ferramentas para desenvolvimento local e empacotamento (PyInstaller).

## Estrutura do projeto (resumo relevante)
- `src/` � c�digo-fonte principal (m�dulos import�veis diretamente). Cont�m:
  - `cli.py` � utilit�rio CLI (pequeno runner de linha de comando)
  - `gfio.py` � utilit�rios de leitura/grava��o de arquivos pipe-delimited (detec��o de encoding)
  - `gui.py` � GUI minimal implementada com PySide6 (prot�tipo)
  - `__init__.py`, `style/` � metadados e estilos
  - `modules/` � m�dulos funcionais organizados como pacotes (ex.: `src/modules/items/`). Cada m�dulo exp�e uma fun��o `panel_widget(parent)` para fornecer o painel da GUI e fun��es utilit�rias como `list_entries(lib_path)`.
- `launch_gfeditor.py` / `launch_gfeditor_gui.py` � launchers que adicionam `src/` ao `sys.path` e iniciam o app
- `run_gfeditor.ps1` � helper PowerShell para criar/ativar venv e rodar a aplica��o no Windows
- `build_exe.ps1` � helper para empacotar com PyInstaller (gera `dist\\GFEditor.exe`)
- `Lib/` � dados do jogo (n�o modifique sem backup)
- `docs/` � documenta��o t�cnica (arquitetura, plugins, contribui��o, roadmap)

## Como rodar (r�pido)
1) Criar e ativar um virtualenv na raiz (Windows PowerShell):
```powershell
python -m venv .venv
. .\\.venv\\Scripts\\Activate.ps1
```
2) Instalar depend�ncias:
```powershell
pip install -r requirements.txt
```
3) Rodar GUI (launcher adiciona `src` ao path):
```powershell
python launch_gfeditor_gui.py
```
ou usar o helper:
```powershell
.\\run_gfeditor.ps1
```

## Suporte a DDS e visualiza��o de �cones

O editor pode exibir os �cones de itens que se encontram em `Assets/itemicon`. Muitos �cones do jogo est�o no formato DDS, que nem sempre � suportado nativamente por todas as plataformas/pluguins do Pillow.

Recomenda��es para garantir visualiza��o de DDS dentro do app:

- Instale `Pillow` no seu ambiente (j� inclu�do em `requirements.txt`).
- Para suporte a DDS mais robusto, instale uma das ferramentas externas abaixo � o app usa essas ferramentas como fallback para converter DDS em PNG e depois exibir:
  - ImageMagick (`magick`) � f�cil de instalar no Windows via instalador oficial ou Chocolatey.
  - texconv (DirectXTex) � utilit�rio da Microsoft/DirectXTex que converte DDS para PNG.

O comportamento implementado no app:
- Tenta carregar imagens diretamente com Qt/QPixmap (r�pido para PNG/JPG).
- Se falhar, tenta abrir com Pillow e converter em mem�ria.
- Se Pillow n�o suportar o DDS presente, tenta usar `magick` ou `texconv` para converter o arquivo para PNG.
- O PNG convertido � armazenado em um cache tempor�rio durante a execu��o do app e � removido automaticamente quando o app fecha (cache por execu��o para evitar arquivos permanentes inesperados).

Se preferir, voc� pode pr�-converter todos os DDS para PNG e coloc�-los em `Assets/itemicon` � o app carregar� os PNGs normalmente sem necessidade de convers�o em tempo de execu��o.

## Como empacotar um exe (Windows)
1) Certifique-se que `Lib/` est� na raiz e que o venv tem as depend�ncias instaladas.
2) Rode:
```powershell
.\\build_exe.ps1
```
Depois coloque a pasta `Lib` ao lado do `.exe` em `dist\\GFEditor\\`.

## Design modular e pontos de extens�o
- O n�cleo exp�e fun��es de IO em `src/gfio.py`. Parsers/transforma��es devem ser implementados como m�dulos separados com interface simples (read -> model -> write).
- Plugins podem ser colocados em `src/plugins/` e descobertos por nome (convencionar um `entrypoint` simples).
- Documenta��o sobre plugins e API est� em `docs/plugins.md`.

## Como criar um novo m�dulo
- Crie uma pasta em `src/modules/<nome>/` e adicione um `__init__.py`.
- Exponha pelo menos:
  - `def panel_widget(parent) -> QWidget`: retorna o widget que ser� mostrado no painel direito.
  - `def list_entries(lib_path: pathlib.Path) -> list[str]`: opcional, retorna itens ou arquivos gerenciados pelo m�dulo.
- Exemplo m�nimo (`src/modules/example/__init__.py`):

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

## Contribuindo
- Veja `docs/contributing.md` para instru��es de desenvolvimento, testes e estilo.

## Licen�a & notas
- Este � um prot�tipo. Fa�a backups de `Lib/` antes de salvar qualquer altera��o.
