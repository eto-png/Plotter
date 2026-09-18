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
                dt_venda DATE,
                nr_parcelas INTEGER,
                vl_total DECIMAL(10,2),
                vl_desconto DECIMAL(10,2),
                ds_observacao TEXT,
                FOREIGN KEY (cd_localidade) REFERENCES localidade(cd_localidade),
                FOREIGN KEY (cd_vendedor) REFERENCES vendedor(cd_vendedor)
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
    