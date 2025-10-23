## Plugins

O GFEditor suporta plugins para adicionar parsers e validadores.

Formato sugerido para plugin:

- `src/plugins/<plugin_name>/__init__.py` deve expor `register()` que retorna um dicion�rio com metadados e fun��es `read`/`write`.

Exemplo m�nimo:

```python
def register():
    return {
        'name': 'example',
        'read': lambda path, encoding=None: [],
        'write': lambda path, data, encoding=None: None,
    }
```

O core pode descobrir plugins importando `src.plugins` e chamando `register()`.
