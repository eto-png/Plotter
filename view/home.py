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

        #Criação do "titulo" do home
        label1_home = QtWidgets.QLabel("Bem vindo ao Plotter!")
        label1_home.setAlignment(QtCore.Qt.AlignCenter)
        #Criação da linha
        row = QtWidgets.QWidget()
        row.setFixedHeight(3)
        row.setFixedWidth(100)
        row.setObjectName("linha")
        #Criação da instrução
        label2_home = QtWidgets.QLabel("Arraste sua planilha de vendas aqui ou clique no botão para fazer o upload")
        label2_home.setAlignment(QtCore.Qt.AlignCenter)

        #Adicionando elementos no layout
        layout_home.addStretch()
        layout_home.addWidget(label1_home)
        layout_home.addWidget(row, alignment= QtCore.Qt.AlignCenter)
        layout_home.addWidget(label2_home)
        layout_home.addStretch()