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
                dt_inauguracao DATE
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
                nm_vendedor VARCHAR(100),
                nr_matricula VARCHAR(20),
                ds_email VARCHAR(150),
                nr_telefone VARCHAR(11),
                dt_admissao DATE,
                dt_demissao DATE
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
                nm_cliente VARCHAR(100),
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
                           nm_cidade: str = "", nm_bairro: str = "", nr_cep: str = "", dt_inauguracao: str = ""):
        sql = '''INSERT INTO localidade (nm_localidade, ds_endereco, sg_estado, nm_cidade, 
                                         nm_bairro, nr_cep, dt_inauguracao) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (nm_localidade, ds_endereco, sg_estado, nm_cidade, 
                                           nm_bairro, nr_cep, dt_inauguracao))

    def inserir_forma_pagamento(self, nm_forma_pagamento: str = ""):
        sql = '''INSERT INTO forma_pagamento (nm_forma_pagamento) 
                 VALUES (?)'''
        return self._executar_insert(sql, (nm_forma_pagamento,))

    # =========================================================
    # 2. TABELAS COM CHAVES ESTRANGEIRAS
    # =========================================================

    def inserir_vendedor(self, nm_vendedor: str = "", nr_matricula: str = "", 
                         ds_email: str = "", nr_telefone: str = "", dt_admissao: str = "", dt_demissao: str = ""):
        sql = '''INSERT INTO vendedor (nm_vendedor, nr_matricula, ds_email, 
                                       nr_telefone, dt_admissao, dt_demissao) 
                 VALUES (?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (nm_vendedor, nr_matricula,
                                           ds_email, nr_telefone, dt_admissao, dt_demissao))

    def inserir_venda(self, cd_localidade: int = 0, cd_vendedor: int = 0, cd_forma_pagamento: int = 0, 
                      dt_venda: str = "", nr_parcelas: int = 0, vl_total: float = 0.0, vl_desconto: float = 0.0, ds_observacao: str = "", nm_cliente: str = ""):
        sql = '''INSERT INTO venda (cd_localidade, cd_vendedor, cd_forma_pagamento, dt_venda, 
                                    nr_parcelas, vl_total, vl_desconto, ds_observacao, nm_cliente) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (cd_localidade, cd_vendedor, cd_forma_pagamento, dt_venda, 
                                           nr_parcelas, vl_total, vl_desconto, ds_observacao, nm_cliente))

    # =========================================================
    # 3. TABELAS DE ASSOCIAÇÃO (Relacionamentos N:M)
    # =========================================================

    def inserir_lista_produtos(self, cd_venda: int = 0, cd_produto: int = 0, qt_produto: int = 0, 
                               vl_unitario: float = 0.0, pc_desconto_unitario: int = 0):
        sql = '''INSERT INTO lista_produtos (cd_venda, cd_produto, qt_produto, vl_unitario, 
                                             pc_desconto_unitario) 
                 VALUES (?, ?, ?, ?, ?)'''
        return self._executar_insert(sql, (cd_venda, cd_produto, qt_produto, vl_unitario, 
                                           pc_desconto_unitario))

    def inserir_lista_categoria(self, categoria_cd_categoria: int = 0, produto_cd_produto: int = 0):
        sql = '''INSERT INTO lista_categoria (categoria_cd_categoria, produto_cd_produto) 
                 VALUES (?, ?)'''
        return self._executar_insert(sql, (categoria_cd_categoria, produto_cd_produto))

    # =========================================================
    # 4. SELECTS NECESSÁRIOS PARA VENDA
    # =========================================================

    def pegar_produto(self, nm_produto: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM produto WHERE nm_produto = ?", (nm_produto,))
            row = cursor.fetchone()
            if row:
                return {
                    "cd_produto": row[0],
                    "nm_produto": row[1],
                    "ds_produto": row[2],
                    "vl_preco": row[3],
                    "vl_custo": row[4]
                }
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar produto: {e}")
            return None

    def pegar_forma_pagamento(self, nm_forma_pagamento: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM forma_pagamento WHERE nm_forma_pagamento = ?", (nm_forma_pagamento,))
            row = cursor.fetchone()
            if row:
                return {
                    "cd_forma_pagamento": row[0],
                    "nm_forma_pagamento": row[1]
                }
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar forma de pagamento: {e}")
            return None

    def pegar_localidade(self, nm_localidade: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM localidade WHERE nm_localidade = ?", (nm_localidade,))
            row = cursor.fetchone()
            if row:
                return {
                    "cd_localidade": row[0],
                    "nm_localidade": row[1],
                    "ds_endereco": row[2],
                    "sg_estado": row[3],
                    "nm_cidade": row[4],
                    "nm_bairro": row[5],
                    "nr_cep": row[6],
                    "dt_inauguracao": row[7]
                }
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar localidade: {e}")
            return None

    def pegar_vendedor(self, nm_vendedor: str):
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM vendedor WHERE nm_vendedor = ?", (nm_vendedor,))
                row = cursor.fetchone()
                if row:
                    return {
                        "cd_vendedor": row[0],
                        "nm_vendedor": row[1],
                        "nr_matricula": row[2],
                        "ds_email": row[3],
                        "dt_demissao": row[4]
                    }
                return None
            except sqlite3.Error as e:
                print(f"Erro ao buscar vendedor: {e}")
                return None

    def prox_cd_venda(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MAX(cd_venda) FROM venda")
            row = cursor.fetchone()
            if row and row[0] is not None:
                return row[0] + 1
            return 1
        except sqlite3.Error as e:
            print(f"Erro ao buscar próximo código de venda: {e}")
            return None