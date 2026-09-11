from model.Produto import Produto

class Produtos:
    def __init__(self, produto, quantidade, preco, desconto):
        self.produto : Produto = produto
        self.quantidade = quantidade
        self.preco = preco
        self.desconto = desconto
