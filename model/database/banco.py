import sqlite3

from config.paths import DASHBOARDS_DIR

class Banco:

    def __init__(self, nome_dashboard : str):
        self.db_path = DASHBOARDS_DIR / f"{nome_dashboard}.db"
        self.connection = ""

    def conectar(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            return self.connection
        
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco {self.db_path}: {e}")
            return None

    def desconectar(self):
        if self.connection: self.connection.close()

    #TODO: Implementar a criação das tabelas no banco de dados
    def inicializar_tabelas(self):

        try:
            cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Não existe conexão aberta com {self.db_path}: {e}")
            return None

        cursor.execute('PRAGMA foreign_keys = ON;')

        # =========================================================
        # 1. TABELAS SEM CHAVES ESTRANGEIRAS (Criadas primeiro)
        # =========================================================
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produto (
                cd_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                nm_produto VARCHAR(150) NOT NULL,
                ds_produto TEXT,
                vl_preco DECIMAL(10,2),
                vl_custo DECIMAL(10,2)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categoria (
                cd_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nm_categoria VARCHAR(20),
                ds_categoria TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS localidade (
                cd_localidade INTEGER PRIMARY KEY AUTOINCREMENT,
                nm_localidade VARCHAR(100),
                ds_endereco VARCHAR(200),
                sg_estado VARCHAR(2),
                nm_cidade VARCHAR(45),
                nm_bairro VARCHAR(45),
                nr_cep VARCHAR(8),
                dt_inauguracao DATE,
                localidadecol VARCHAR(45)
            )
        ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS forma_pagamento (
                        cd_forma_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
                        nm_forma_pagamento VARCHAR(100)
                    )
                ''')

        # =========================================================
        # 2. TABELAS COM CHAVES ESTRANGEIRAS
        # =========================================================

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendedor (
                cd_vendedor INTEGER PRIMARY KEY AUTOINCREMENT,
                cd_localidade INTEGER,
                nm_vendedor VARCHAR(100),
                nr_matricula VARCHAR(20),
                ds_email VARCHAR(150),
                nr_telefone VARCHAR(11),
                dt_admissao DATE,
                dt_demissao DATE,
                FOREIGN KEY (cd_localidade) REFERENCES localidade(cd_localidade)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS venda (
                cd_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                cd_localidade INTEGER,
                cd_vendedor INTEGER,
                cd_forma_pagamento INTEGER,
                dt_venda DATE,
                nr_parcelas INTEGER,
                vl_total DECIMAL(10,2),
                vl_desconto DECIMAL(10,2),
                ds_observacao TEXT,
                FOREIGN KEY (cd_localidade) REFERENCES localidade(cd_localidade),
                FOREIGN KEY (cd_vendedor) REFERENCES vendedor(cd_vendedor),
                FOREIGN KEY (cd_forma_pagamento) REFERENCES forma_pagamento(cd_forma_pagamento)
            )
        ''')

        # =========================================================
        # 3. TABELAS DE ASSOCIAÇÃO (Relacionamentos N:M)
        # =========================================================

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lista_produtos (
                cd_venda INTEGER,
                cd_produto INTEGER,
                qt_produto INTEGER,
                vl_unitario DECIMAL(10,2),
                pc_desconto_unitario INTEGER,
                lista_produtoscol VARCHAR(45),
                PRIMARY KEY (cd_venda, cd_produto),
                FOREIGN KEY (cd_venda) REFERENCES venda(cd_venda),
                FOREIGN KEY (cd_produto) REFERENCES produto(cd_produto)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lista_categoria (
                categoria_cd_categoria INTEGER,
                produto_cd_produto INTEGER,
                PRIMARY KEY (categoria_cd_categoria, produto_cd_produto),
                FOREIGN KEY (categoria_cd_categoria) REFERENCES categoria(cd_categoria),
                FOREIGN KEY (produto_cd_produto) REFERENCES produto(cd_produto)
            )
        ''')

        # Salva as alterações no arquivo .db
        self.connection.commit()

        return

import sqlite3
from typing import Optional

class BancoOperacoes(Banco):
    def __init__(self, nome_dashboard: str = ""):
        super().__init__(nome_dashboard)
        
    def _executar_insert(self, sql: str, parametros: tuple):
        if not self.connection:
            self.conectar()
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, parametros)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao inserir dados: {e}")
            self.connection.rollback()
            return None

    # =========================================================
    # 1. TABELAS SEM CHAVES ESTRANGEIRAS
    # =========================================================

    def inserir_produto(self, nm_produto: str = "", ds_produto: str = "", vl_preco: float = 0.0, vl_custo: float = 0.0):
        sql = '''INSERT INTO produto (nm_produto, ds_produto, vl_preco, vl_custo) 
                 VALUES (?, ?, ?, ?)'''
        return self._executar_insert(sql, (nm_produto, ds_produto, vl_preco, vl_custo))

    def inserir_categoria(self, nm_categoria: str = "", ds_categoria: str = ""):
        sql = '''INSERT INTO categoria (nm_categoria, ds_categoria) 
                 VALUES (?, ?)'''
        return self._executar_insert(sql, (nm_categoria, ds_categoria))

    def inserir_localidade(self, nm_localidade: str = "", ds_endereco: str = "", sg_estado: str = "", 
                           nm_cidade: str = "", nm_bairro: str = "", nr_cep: str = "", dt_inauguracao: str = "", localidadecol: str = ""):
        sql = '''INSERT INTO localidade (nm_localidade, ds_endereco, sg_estado, nm_cidade, 
                                         nm_bairro, nr_cep, dt_inauguracao, localidadecol) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (nm_localidade, ds_endereco, sg_estado, nm_cidade, 
                                           nm_bairro, nr_cep, dt_inauguracao, localidadecol))

    def inserir_forma_pagamento(self, nm_forma_pagamento: str = ""):
        sql = '''INSERT INTO forma_pagamento (nm_forma_pagamento) 
                 VALUES (?)'''
        return self._executar_insert(sql, (nm_forma_pagamento,))

    # =========================================================
    # 2. TABELAS COM CHAVES ESTRANGEIRAS
    # =========================================================

    def inserir_vendedor(self, cd_localidade: int = 0, nm_vendedor: str = "", nr_matricula: str = "", 
                         ds_email: str = "", nr_telefone: str = "", dt_admissao: str = "", dt_demissao: str = ""):
        sql = '''INSERT INTO vendedor (cd_localidade, nm_vendedor, nr_matricula, ds_email, 
                                       nr_telefone, dt_admissao, dt_demissao) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (cd_localidade, nm_vendedor, nr_matricula, 
                                           ds_email, nr_telefone, dt_admissao, dt_demissao))

    def inserir_venda(self, cd_localidade: int = 0, cd_vendedor: int = 0, cd_forma_pagamento: int = 0, 
                      dt_venda: str = "", nr_parcelas: int = 0, vl_total: float = 0.0, vl_desconto: float = 0.0, ds_observacao: str = ""):
        sql = '''INSERT INTO venda (cd_localidade, cd_vendedor, cd_forma_pagamento, dt_venda, 
                                    nr_parcelas, vl_total, vl_desconto, ds_observacao) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (cd_localidade, cd_vendedor, cd_forma_pagamento, dt_venda, 
                                           nr_parcelas, vl_total, vl_desconto, ds_observacao))

    # =========================================================
    # 3. TABELAS DE ASSOCIAÇÃO (Relacionamentos N:M)
    # =========================================================

    def inserir_lista_produtos(self, cd_venda: int = 0, cd_produto: int = 0, qt_produto: int = 0, 
                               vl_unitario: float = 0.0, pc_desconto_unitario: int = 0, lista_produtoscol: str = ""):
        sql = '''INSERT INTO lista_produtos (cd_venda, cd_produto, qt_produto, vl_unitario, 
                                             pc_desconto_unitario, lista_produtoscol) 
                 VALUES (?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (cd_venda, cd_produto, qt_produto, vl_unitario, 
                                           pc_desconto_unitario, lista_produtoscol))

    def inserir_lista_categoria(self, categoria_cd_categoria: int = 0, produto_cd_produto: int = 0):
        sql = '''INSERT INTO lista_categoria (categoria_cd_categoria, produto_cd_produto) 
                 VALUES (?, ?)'''
        return self._executar_insert(sql, (categoria_cd_categoria, produto_cd_produto))