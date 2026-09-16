# model/entities/__init__.py

from .venda import Venda
from .produto import Produto
from .categoria import Categoria
from .localidade import Localidade
from .produtos import Produtos
from .vendedor import Vendedor

__all__ = [
    'Venda',
    'Produto',
    'Categoria',
    'Localidade',
    'Produto',
    'Produtos',
    'Vendedor',
]