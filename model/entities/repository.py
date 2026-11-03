import pandas as pd
import re

from model.database import banco
from model.database.banco import BancoOperacoes

class GenericDatabaseRepository:
    def __init__(self, nome_dashboard):
        self.banco = BancoOperacoes(nome_dashboard)

    def inserir_extremidades(self, df: pd.DataFrame, mapa: dict):

        self.banco.conectar()
        self.banco.inicializar_tabelas()

         
        for coluna, tabela in mapa.items():
            print(f"{coluna}: {tabela}")
            if tabela is not None:
                for linha in df[coluna].unique():
                    # print(df[coluna].unique())
                    if linha is None or pd.isna(linha): continue
                    match tabela:
                        case "produto":
                            padrao_valor_unitario = r"(?i)\b(valor|val|vlr|vl|vr|pre[çc]o)[\s_\-\.]*(unit[aá]rio|unit|unt|un)\b"
                            valor_unitario = None

                            padrao_valor_custo = r"(?i)\b((valor|val|vlr|vl|vr|pre[çc]o)[\s_\-\.]*)?(custo|cst)\b"
                            valor_custo = None

                            padrao_obs_ds = r"(?i)\b(descri[çc][aã]o|desc|observa[çc][aã]o|obs)\b"
                            ds_obs = None
                            
                            for col in df.columns:
                                if re.search(padrao_valor_unitario, col):
                                    valor_unitario = df.loc[df[coluna] == linha, col].values[0]
                                    continue
                            
                                if re.search(padrao_valor_custo, col):
                                    valor_custo = df.loc[df[coluna] == linha, col].values[0]
                                    continue

                                if re.search(padrao_obs_ds, col):
                                    ds_obs = df.loc[df[coluna] == linha, col].values[0]
                                    continue

                            self.banco.inserir_produto(str(linha), ds_obs, valor_unitario, valor_custo)
                            
                        case "categoria":
                            self.banco.inserir_categoria(str(linha))
                            
                        case "localidade":
                            self.banco.inserir_localidade(str(linha))
                            #TODO: Implementar a inserção de localidade com base em cidade, estado e país
                            
                        case "vendedor":
                            self.banco.inserir_vendedor(str(linha))
                            
                        case "forma_pagamento":
                            self.banco.inserir_forma_pagamento(str(linha))
        
        self.banco.desconectar()

    def inserir_vendas(self, df: pd.DataFrame, mapa : dict):
        
        self.banco.conectar()

        col_produto = None
        col_localidade = None
        col_vendedor = None
        col_forma_pagamento = None

        for coluna, tabela in mapa.items():
            match tabela:
                case "produto":
                    col_produto = coluna
                case "localidade":
                    col_localidade = coluna
                case "vendedor":
                    col_vendedor = coluna
                case "forma_pagamento":
                    col_forma_pagamento = coluna

        #venda
        col_dt_venda = None
        col_nr_parcelas = None
        col_vl_total = None
        col_vl_desconto = None
        col_ds_observacao = None
        col_nm_cliente = None

        #lista_produtos
        col_qt_produto = None
        col_vl_unitario = None
        col_desconto_unitario = None

        for coluna in df.columns.to_list():
            #venda
            if coluna.lower() in ["data", "dt_venda", "data_venda"]:
                col_dt_venda = coluna ; continue
            if coluna.lower() in ["parcelas", "nr_parcelas", "numero_parcelas"]:
                col_nr_parcelas = coluna ; continue 
            if coluna.lower() in ["total", "vl_total", "valor_total"]:
                col_vl_total = coluna ; continue
            if coluna.lower() in ["desconto", "vl_desconto", "valor_desconto"]:
                col_vl_desconto = coluna ; continue
            if coluna.lower() in ["observacao", "ds_observacao", "descricao_observacao", "obs"]:
                col_ds_observacao = coluna ; continue
            if coluna.lower() in ["cliente", "nm_cliente", "nome_cliente", "empresa"]:
                col_nm_cliente = coluna ; continue

            #lista_produtos
            if coluna.lower() in ["quantidade", "qt_produto", "quantidade_produto"]:
                col_qt_produto = coluna ; continue
            if coluna.lower() in ["valor_unitario", "vl_unitario", "valor_unitario_produto"]:
                col_vl_unitario = coluna ; continue
            if coluna.lower() in ["desconto_unitario", "pc_desconto_unitario", "percentual_desconto_unitario"]:
                col_desconto_unitario = coluna ; continue

        print(col_dt_venda)

        for index, row in df.iterrows():

            nm_produto = row.get(col_produto, None)
            if nm_produto is None or pd.isna(nm_produto): 
                print(f"Produto não encontrado na linha {index + 1}. Pulando...")
                continue

            # print("Pegando o código do produto:", nm_produto)
            cd_produto = self.banco.pegar_produto(nm_produto)["cd_produto"]
            cd_venda = self.banco.prox_cd_venda() # pega o codigo de venda que será inserido

            cd_localidade = row.get(col_localidade, None)

            nm_vendedor = row.get(col_vendedor, None)
            # print("Pegando o código do vendedor:", nm_vendedor)
            cd_vendedor = self.banco.pegar_vendedor(nm_vendedor)["cd_vendedor"]

            cd_forma_pagamento = row.get(col_forma_pagamento, None)
            dt_venda = row.get(col_dt_venda, None).strftime('%Y-%m-%d')
            nr_parcelas = row.get(col_nr_parcelas, None)
            vl_total = row.get(col_vl_total, None)
            vl_desconto = row.get(col_vl_desconto, None)
            ds_observacao = row.get(col_ds_observacao, None)
            nm_cliente = row.get(col_nm_cliente, None)

            self.banco.inserir_venda(cd_localidade, cd_vendedor, cd_forma_pagamento, dt_venda, nr_parcelas, vl_total, vl_desconto, ds_observacao, nm_cliente)

            lista_produto = (cd_produto, cd_venda)
             # (cd_produto, cd_venda)

            qt_produto = row.get(col_qt_produto, None)
            vl_unitario = row.get(col_vl_unitario, None)
            pc_desconto_unitario = row.get(col_desconto_unitario, None) 

            self.banco.inserir_lista_produtos(lista_produto[0], lista_produto[1], qt_produto, vl_unitario, pc_desconto_unitario)

        self.banco.desconectar()
        