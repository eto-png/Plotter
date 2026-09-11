from model.entities.Produtos import Produtos
from model.entities.Localidade import Localidade

class Venda:
    def __init__(self, produtos, localidade, dt_venda, qt_parcelas, obs):
        self.produtos = produtos
        self.localidade = localidade
        self.dt_venda = dt_venda
        self.calcular_desconto()
        self.calcular_total()
        self.qt_parcelas = qt_parcelas
        self.obs = obs
        

    def caluclar_desconto(self):
        total_desconto = 0
        for produto in self.produtos:
            total_desconto += produto.desconto
        self.desconto = total_desconto

    def calcular_total(self):
        total = 0
        for produto in self.produtos:
            total += produto.preco * produto.quantidade
        self.total = total - self.desconto