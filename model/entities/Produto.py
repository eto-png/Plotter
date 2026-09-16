from model.entities.categoria import Categoria

class Produto:
    
    def __init__(self, nome, descricao, preco, categorias : list[Categoria]):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.categorias : list[Categoria] = categorias
        