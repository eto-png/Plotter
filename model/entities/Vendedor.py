from model.entities.Localidade import Localidade

class Vendedor:
    
    def __init__(self, nome, matricula, email, telefone, dt_admissao, dt_demissao, localidade):
        self.nome = nome
        self.matricula = matricula
        self.email = email
        self.telefone = telefone
        self.dt_admissao = dt_admissao
        self.dt_demissao = dt_demissao
        self.localidade : Localidade = localidade
