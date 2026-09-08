import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

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
        label1_home = QtWidgets.QLabel("Bem vindo ao Plotter!")
        label1_home.setAlignment(QtCore.Qt.AlignCenter)
        label1_home.setObjectName("labelTitulo")

        #Criação da linha
        row = QtWidgets.QWidget()
        row.setFixedHeight(2)
        row.setFixedWidth(705)
        row.setObjectName("linha")

        #Criação da instrução
        label2_home = QtWidgets.QLabel("Arraste sua planilha de vendas aqui ou clique\n no botão para fazer o upload")
        label2_home.setAlignment(QtCore.Qt.AlignCenter)
        label2_home.setObjectName("labelTexto")
        label2_home.setWordWrap(True) #ativa quabra de linha

        #Criação do botão de upload de arquivo
        btnUpload = QtWidgets.QPushButton()
        btnUpload.setObjectName("btnUpload")
        btnUpload.setIcon(QtGui.QIcon("images/plus.svg"))
        btnUpload.setIconSize(QtCore.QSize(64, 64))
        btnUpload.setFixedSize(108, 108)
        btnUpload.clicked.connect(self.open_explorer)

        #Adicionando elementos no layout
        layout_home.addStretch()
        layout_home.addWidget(label1_home)
        layout_home.addWidget(row, alignment= QtCore.Qt.AlignCenter)
        layout_home.addWidget(label2_home)
        layout_home.addWidget(btnUpload, alignment= QtCore.Qt.AlignCenter)
        layout_home.addStretch()

    #Função para abrir o explorador de arquivos e selecionar o arquivo.
    def open_explorer(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecione a planilha", "", "Arquivos de Excel (*.xlsx *.xls)")

        if filePath:
            print(f"Arquivo selecionado: {filePath}")