"""Package for GUI modules.

This package exposes submodules (items, monsters, npcs, shops) so imports like
`modules.items` continue to work after we turn each module into a subpackage.
"""
from importlib import import_module

__all__ = [
    'items',
    'monsters',
    'npcs',
    'shops',
]

# lazy import attributes for convenience
def __getattr__(name):
    if name in __all__:
        mod = import_module(f'{__package__}.{name}')
        globals()[name] = mod
        return mod
    raise AttributeError(name)
