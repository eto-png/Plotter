from model.entities.Categoria import Categoria

class Produto:
    
    def __init__(self, nome, descricao, preco, categorias):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.categorias : list[Categoria] = categorias
        