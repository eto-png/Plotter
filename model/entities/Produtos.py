from model.entities.produto import Produto

class Produtos:
    def __init__(self, produto : Produto, preco : float = 0, quantidade : int = 0, desconto : int = 0):
        self.produto : Produto = produto
        self.quantidade = quantidade
        if preco == 0: self.preco = self.quantidade * self.produto.preco
        else: self.preco = preco
        self.desconto = desconto
