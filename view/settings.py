import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

from config.paths import IMAGES_DIR

class Settings(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #Cria o conteudo da pagina
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) #Faz com que o QSS seja aplicado nessa subclasse
        self.setObjectName("conteudo")

        #Cria o layout principal da tela
        layout_settings = QtWidgets.QVBoxLayout(self)
        layout_settings.setSpacing(0)
        layout_settings.setContentsMargins(0, 0, 0, 0)

        #Cria o "titulo" da pagina
        label_title = QtWidgets.QLabel("CONFIGURAÇÕES")
        label_title.setAlignment(QtCore.Qt.AlignCenter)
        label_title.setObjectName("settingsTitle")

        #Cria a "div" que contém os cards de opções
        settings_container = QtWidgets.QFrame()
        settings_container.setObjectName("settingsDiv")

        #Cria o layout da div
        layout_container = QtWidgets.QVBoxLayout(settings_container)
        layout_container.setContentsMargins(30, 30, 30, 30)
        layout_container.setSpacing(20)

        #Cria o layout de cada linha da div
        row1 = QtWidgets.QHBoxLayout()
        row2 = QtWidgets.QHBoxLayout()
        row3 = QtWidgets.QHBoxLayout()

        #Cria o card da opção "Tema" e seus elementos
        card_tema, layout_tema = self.new_card(f"{IMAGES_DIR}/paint-brush.svg", "Tema", "Escolha o modo visual da interface")
        btnDark = QtWidgets.QPushButton("Escuro") #Criação dos botões do "Tema"
        btnDark.setObjectName("btnDark")
        btnLight = QtWidgets.QPushButton("Claro")
        btnLight.setObjectName("btnLight")
        btnSystem = QtWidgets.QPushButton("Sistema")
        btnSystem.setObjectName("btnSystem")

        btnDark.setCheckable(True) #Permite os botões serem checaveis
        btnLight.setCheckable(True)
        btnSystem.setCheckable(True)

        group_tema = QtWidgets.QButtonGroup(self) #Criação do grupo de botões
        group_tema.setExclusive(True) #Permite exclusividade na seleção do botão, permitindo so 1 por vez

        group_tema.addButton(btnDark) #Adiciona os botões ao grupo
        group_tema.addButton(btnLight)
        group_tema.addButton(btnSystem)

        btnDark.setChecked(True) #Faz o botão dark começar selecionado

        layout_btn_tema = QtWidgets.QHBoxLayout() #Cria o layout horizontal para os botões
        layout_btn_tema.addWidget(btnDark) #Adiciona os botões ao layout
        layout_btn_tema.addWidget(btnLight)
        layout_btn_tema.addWidget(btnSystem)

        layout_tema.addLayout(layout_btn_tema) #Adiciona o layout dos botões ao layout do card "Tema"
        row1.addWidget(card_tema) #Adiciona o card "Tema" na primeira linha


        #Criação do card "Nivel de analise"
        #ATENÇÃO: ta faltando fazer a animação dos botões, dei uma olhada e fiz uns testes mas putaquepariu que dor de cabeça do caralho pra fazer essa merda funcionar.
        card_analise, layout_analise = self.new_card(f"{IMAGES_DIR}/brain-circuit.svg", "Nível de análise", "Nível de análise da IA")

        container_analise = QtWidgets.QWidget() #Criação do container que engloba os botões

        layout_container_analise = QtWidgets.QVBoxLayout(container_analise) #Criação do layout para o container, fazendo com que seja mais facil de englobar por um todo o conteudo
        layout_container_analise.setContentsMargins(2, 2, 2, 2)
        layout_container_analise.setSpacing(0)

        #indicator_analise = QtWidgets.QFrame(container_analise) #Criação do frame que fica de fundo do botão selecionado
        #indicator_analise.setObjectName("indicatorAnalise")

        border_analise = QtWidgets.QFrame(container_analise) #Criação do frame para fazer a borda que engloba os botões
        border_analise.setObjectName("borderAnalise")

        layout_container_analise.addWidget(border_analise) #Adiciona o frame de borda ao layout do container

        btnFast = QtWidgets.QPushButton("Rápido") #Criação dos botões do card "Analise"
        btnStandard = QtWidgets.QPushButton("Padrão")
        btnDetailed = QtWidgets.QPushButton("Detalhado")

        btnFast.setCheckable(True) #Permite os botões serem checaveis
        btnStandard.setCheckable(True)
        btnDetailed.setCheckable(True)

        group_analise = QtWidgets.QButtonGroup(self) #Criação do grupo de botões do card
        group_analise.setExclusive(True) #Permite exclusividade na seleção do botão, permitindo so 1 por vez

        group_analise.addButton(btnFast) #Adiciona os botões ao grupo
        group_analise.addButton(btnStandard)
        group_analise.addButton(btnDetailed)

        btnStandard.setChecked(True) #Faz o botão "Padrão" ser o ativado por padrão

        layout_btn_analise = QtWidgets.QHBoxLayout(border_analise) #Criação do layout horizontal para os botões
        layout_btn_analise.addWidget(btnFast) #Adiciona os botões ao layout criado acima
        layout_btn_analise.addWidget(btnStandard)
        layout_btn_analise.addWidget(btnDetailed)

        layout_analise.addWidget(container_analise) #Adiciona o container ao layout principal do card
        row1.addWidget(card_analise) #Adiciona o card na linha 1


        #Criação do card "Linguagem"
        card_linguagem, layout_linguagem = self.new_card(f"{IMAGES_DIR}/translate.svg", "Linguagem", "Linguagem do aplicativo")

        combo_language = QtWidgets.QComboBox()
        combo_language.setFixedHeight(38)
        combo_language.addItems(["Português (Brasil)", "Inglês (US)"])
        combo_language.setCurrentText("Português (Brasil)")

        layout_linguagem.addWidget(combo_language)
        row2.addWidget(card_linguagem)


        #Criação do card "Data"
        card_data, layout_data = self.new_card(f"{IMAGES_DIR}/calendar.svg", "Data", "Formato de data")
        
        combo_data = QtWidgets.QComboBox()
        combo_data.setFixedHeight(38)
        combo_data.addItems(["DD/MM/AAAA", "MM/DD/AAAA", "DD-MM-AAAA"])
        combo_data.setCurrentText("DD/MM/AAAA")
        
        layout_data.addWidget(combo_data)
        row2.addWidget(card_data)

        layout_container.addLayout(row1) #Adiciona a primeira linha ao layout da div
        layout_container.addLayout(row2)

        #Adiciona os elementos ao layout principal
        layout_settings.addWidget(label_title)
        layout_settings.addWidget(settings_container)
        layout_settings.addStretch()

        buttons = [btnDark, btnLight, btnSystem, btnFast, btnStandard, btnDetailed, combo_language]
        for btn in buttons:
            btn.setCursor(QtCore.Qt.PointingHandCursor)

    #Função que cria um card genérico para as opções
    def new_card(self, icon_path: str, title: str, desc: str) -> tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
        card = QtWidgets.QFrame()
        card.setObjectName("cardSettings")

        layout_card = QtWidgets.QVBoxLayout(card)
        layout_card.setContentsMargins(20, 20, 20, 20)
        layout_card.setSpacing(10)

        layout_header = QtWidgets.QHBoxLayout()
        layout_header.setSpacing(10)

        card_icon = QtWidgets.QLabel()
        card_icon.setPixmap(QtGui.QPixmap(icon_path).scaled(20, 20, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        card_title = QtWidgets.QLabel(title.upper())
        card_title.setObjectName("cardTitle")

        layout_header.addWidget(card_icon)
        layout_header.addWidget(card_title)
        layout_header.addStretch()

        card_desc = QtWidgets.QLabel(desc)
        card_desc.setObjectName("cardDesc")

        layout_card.addLayout(layout_header)
        layout_card.addWidget(card_desc)

        return card, layout_card

