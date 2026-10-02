import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from config.locales import languages

from config.paths import IMAGES_DIR

class Home(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #Cria o conteudo da pagina
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) #Faz com que o QSS seja aplicado nessa subclasse
        self.setObjectName("conteudo")

        layout_home = QtWidgets.QVBoxLayout(self)
        layout_home.setSpacing(0)
        layout_home.setContentsMargins(0, 0, 0, 0)

        #Criação do "titulo" do home
        self.label1_home = QtWidgets.QLabel("Bem vindo ao Plotter!")
        self.label1_home.setAlignment(QtCore.Qt.AlignCenter)
        self.label1_home.setObjectName("labelTitulo")

        #Criação da linha
        row = QtWidgets.QWidget()
        row.setFixedHeight(2)
        row.setFixedWidth(705)
        row.setObjectName("linha")
        

        #Criação da instrução
        self.label2_home = QtWidgets.QLabel("Arraste sua planilha de vendas aqui ou clique\n no botão para fazer o upload")
        self.label2_home.setAlignment(QtCore.Qt.AlignCenter)
        self.label2_home.setObjectName("labelTexto")
        self.label2_home.setWordWrap(True) #ativa quabra de linha

        #Criação do botão de upload de arquivo
        self.btnUpload = QtWidgets.QPushButton()
        self.btnUpload.setObjectName("btnUpload")
        self.btnUpload.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/plus.svg"))
        self.btnUpload.setIconSize(QtCore.QSize(64, 64))
        self.btnUpload.setFixedSize(108, 108)
        self.btnUpload.clicked.connect(self.open_explorer)
        self.btnUpload.setCursor(QtCore.Qt.PointingHandCursor)

        #Adicionando elementos no layout
        layout_home.addStretch()
        layout_home.addWidget(self.label1_home)
        layout_home.addWidget(row, alignment= QtCore.Qt.AlignCenter)
        layout_home.addWidget(self.label2_home)
        layout_home.addWidget(self.btnUpload, alignment= QtCore.Qt.AlignCenter)
        layout_home.addStretch()

    #Função para abrir o explorador de arquivos e selecionar o arquivo.
    def open_explorer(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecione a planilha", "", "Arquivos de Excel (*.xlsx *.xls)")

        #Só para testar se ta pegando o caminho do arquivo
        if filePath:
            print(f"Arquivo selecionado: {filePath}")

    #Função para alterar os textos de acordo com o idioma escolhido
    def retranslate(self, lang_code: str):
        texts = languages.get(lang_code, languages["pt_BR"])

        self.label1_home.setText(texts["home_title"])
        self.label2_home.setText(texts["home_txt"])