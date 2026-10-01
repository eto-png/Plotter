import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from view.components.switch import SwitchToggle
from config.locales import languages

from config.paths import IMAGES_DIR

class Settings(QtWidgets.QWidget):
    #Cria um sinal
    theme_changed = QtCore.Signal(str)
    language_changed = QtCore.Signal(str)
    back = QtCore.Signal(int)

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
        self.label_title = QtWidgets.QLabel()
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("settingsTitle")

        #Cria a "div" que contém os cards de opções
        settings_container = QtWidgets.QFrame()
        settings_container.setObjectName("settingsDiv")

        #Cria o layout da div
        layout_container = QtWidgets.QVBoxLayout(settings_container)
        layout_container.setContentsMargins(30, 30, 30, 15)
        layout_container.setSpacing(20)

        #Cria o layout de cada linha da div
        row1 = QtWidgets.QHBoxLayout()
        row2 = QtWidgets.QHBoxLayout()
        row3 = QtWidgets.QHBoxLayout()

        self.translatable_cards = [] #Cria uma lista para guardar as informações das labels dos cards que precisam de tradução

        #Cria o card da opção "Tema" e seus elementos
        card_tema, layout_tema = self.new_card(f"{IMAGES_DIR}/paint-brush.svg", "theme_title", "theme_txt")
        self.btnDark = QtWidgets.QPushButton() #Criação dos botões do "Tema"
        self.btnDark.setObjectName("btnDark")
        self.btnLight = QtWidgets.QPushButton()
        self.btnLight.setObjectName("btnLight")
        self.btnSystem = QtWidgets.QPushButton()
        self.btnSystem.setObjectName("btnSystem")

        #Faz os cliques enviarem um sinal com seu nome
        self.btnDark.clicked.connect(lambda: self.theme_changed.emit("dark"))
        self.btnLight.clicked.connect(lambda: self.theme_changed.emit("light"))
        self.btnSystem.clicked.connect(lambda: self.theme_changed.emit("system"))

        self.btnDark.setCheckable(True) #Permite os botões serem checaveis
        self.btnLight.setCheckable(True)
        self.btnSystem.setCheckable(True)

        group_tema = QtWidgets.QButtonGroup(self) #Criação do grupo de botões
        group_tema.setExclusive(True) #Permite exclusividade na seleção do botão, permitindo so 1 por vez

        group_tema.addButton(self.btnDark) #Adiciona os botões ao grupo
        group_tema.addButton(self.btnLight)
        group_tema.addButton(self.btnSystem)

        self.btnDark.setChecked(True) #Faz o botão dark começar selecionado

        layout_btn_tema = QtWidgets.QHBoxLayout() #Cria o layout horizontal para os botões
        layout_btn_tema.addWidget(self.btnDark) #Adiciona os botões ao layout
        layout_btn_tema.addWidget(self.btnLight)
        layout_btn_tema.addWidget(self.btnSystem)

        layout_tema.addLayout(layout_btn_tema) #Adiciona o layout dos botões ao layout do card "Tema"
        row1.addWidget(card_tema) #Adiciona o card "Tema" na primeira linha


        #Criação do card "Nivel de analise"
        #ATENÇÃO: ta faltando fazer a animação dos botões, dei uma olhada e fiz uns testes mas putaquepariu que dor de cabeça do caralho pra fazer essa merda funcionar.
        card_analise, layout_analise = self.new_card(f"{IMAGES_DIR}/brain-circuit.svg", "analysis_title", "analysis_txt")

        container_analise = QtWidgets.QWidget() #Criação do container que engloba os botões

        layout_container_analise = QtWidgets.QVBoxLayout(container_analise) #Criação do layout para o container, fazendo com que seja mais facil de englobar por um todo o conteudo
        layout_container_analise.setContentsMargins(2, 2, 2, 2)
        layout_container_analise.setSpacing(0)

        #indicator_analise = QtWidgets.QFrame(container_analise) #Criação do frame que fica de fundo do botão selecionado
        #indicator_analise.setObjectName("indicatorAnalise")

        border_analise = QtWidgets.QFrame(container_analise) #Criação do frame para fazer a borda que engloba os botões
        border_analise.setObjectName("borderAnalise")

        layout_container_analise.addWidget(border_analise) #Adiciona o frame de borda ao layout do container

        self.btnFast = QtWidgets.QPushButton() #Criação dos botões do card "Analise"
        self.btnStandard = QtWidgets.QPushButton()
        self.btnDetailed = QtWidgets.QPushButton()

        self.btnFast.setCheckable(True) #Permite os botões serem checaveis
        self.btnStandard.setCheckable(True)
        self.btnDetailed.setCheckable(True)

        group_analise = QtWidgets.QButtonGroup(self) #Criação do grupo de botões do card
        group_analise.setExclusive(True) #Permite exclusividade na seleção do botão, permitindo so 1 por vez

        group_analise.addButton(self.btnFast) #Adiciona os botões ao grupo
        group_analise.addButton(self.btnStandard)
        group_analise.addButton(self.btnDetailed)

        self.btnStandard.setChecked(True) #Faz o botão "Padrão" ser o ativado por padrão

        layout_btn_analise = QtWidgets.QHBoxLayout(border_analise) #Criação do layout horizontal para os botões
        layout_btn_analise.addWidget(self.btnFast) #Adiciona os botões ao layout criado acima
        layout_btn_analise.addWidget(self.btnStandard)
        layout_btn_analise.addWidget(self.btnDetailed)

        layout_analise.addWidget(container_analise) #Adiciona o container ao layout principal do card
        row1.addWidget(card_analise) #Adiciona o card na linha 1


        #Criação do card "Linguagem"
        card_linguagem, layout_linguagem = self.new_card(f"{IMAGES_DIR}/translate.svg", "language_title", "language_txt")

        self.combo_language = QtWidgets.QComboBox()
        self.combo_language.setFixedHeight(38)
        self.combo_language.addItems(["Português (Brasil)", "Inglês (US)"])

        self.lang_map = {
            "Português (Brasil)": "pt_BR",
            "Inglês (US)": "en_US",
            "Portuguese (Brazil)": "pt_BR",
            "English (US)": "en_US"
        }

        self.combo_language.currentTextChanged.connect(self._language_combo_changed)

        layout_linguagem.addWidget(self.combo_language)
        row2.addWidget(card_linguagem) #Adiciona o card na linha 2


        #Criação do card "Data"
        card_data, layout_data = self.new_card(f"{IMAGES_DIR}/calendar.svg", "date_title", "date_txt")
        
        self.combo_data = QtWidgets.QComboBox()
        self.combo_data.setFixedHeight(38)
        self.combo_data.addItems(["DD/MM/AAAA", "MM/DD/AAAA", "DD-MM-AAAA"])
        self.combo_data.setCurrentText("DD/MM/AAAA")
        
        layout_data.addWidget(self.combo_data)
        row2.addWidget(card_data) #Adiciona o card na linha 2


        #Criação do card "Resumo"
        card_resumo, layout_resumo = self.new_card(f"{IMAGES_DIR}/summary.svg", "summary_title", "summary_txt")

        #Instancia o switch toggle
        self.switch_resumo = SwitchToggle()
        self.switch_resumo.setChecked(False)  #Começa desligado

        layout_resumo.addWidget(self.switch_resumo)
        layout_resumo.addStretch()

        row3.addWidget(card_resumo)


        #Criação do card "Separador"
        card_separador, layout_separador = self.new_card(f"{IMAGES_DIR}/file.svg", "separator_title", "separator_txt")

        self.btnComma = QtWidgets.QPushButton() #Cria os botões
        self.btnComma.setObjectName("btnComma")
        self.btnPoint = QtWidgets.QPushButton()
        self.btnPoint.setObjectName("btnPoint")

        self.btnComma.setCheckable(True) #Torna os botões checaveis
        self.btnPoint.setCheckable(True)

        group_separador = QtWidgets.QButtonGroup(self) #Cria o grupo dos botões
        group_separador.setExclusive(True) #Habilita a exclusividade de check nos botões do grupo

        group_separador.addButton(self.btnComma) #Adiciona os botões no grupo
        group_separador.addButton(self.btnPoint)

        self.btnComma.setChecked(True) #Faz o botão de virgula estar checado por padrao

        layout_btn_separador = QtWidgets.QHBoxLayout() #Cria o layout para os botões
        layout_btn_separador.addWidget(self.btnComma) #Adiciona os botões ao layout
        layout_btn_separador.addWidget(self.btnPoint)

        layout_separador.addLayout(layout_btn_separador) #Adiciona o layout dos botões no layout do card
        row3.addWidget(card_separador) #Adiciona o card na linha 3


        self.btnBack = QtWidgets.QPushButton()
        self.btnBack.setFixedSize(100, 40)
        self.btnBack.setObjectName("btnBack")
        self.btnBack.clicked.connect(lambda: self.back.emit(0))


        layout_container.addLayout(row1) #Adiciona a primeira linha ao layout da div
        layout_container.addLayout(row2) #Adiciona a segunda linha ao layout da div
        layout_container.addLayout(row3) #Adiciona a terceira linha ao layout da div
        layout_container.addWidget(self.btnBack, alignment= QtCore.Qt.AlignCenter)

        #Adiciona os elementos ao layout principal
        layout_settings.addWidget(self.label_title)
        layout_settings.addWidget(settings_container)
        layout_settings.addStretch()

        buttons = [self.btnDark, self.btnLight, self.btnSystem, self.btnFast, self.btnStandard, self.btnDetailed, self.combo_language, self.combo_data, self.btnComma, self.btnPoint, self.btnBack]
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

        card_title = QtWidgets.QLabel()
        card_title.setObjectName("cardTitle")

        layout_header.addWidget(card_icon)
        layout_header.addWidget(card_title)
        layout_header.addStretch()

        card_desc = QtWidgets.QLabel()
        card_desc.setObjectName("cardDesc")

        layout_card.addLayout(layout_header)
        layout_card.addWidget(card_desc)

        self.translatable_cards.append({
            "title_label": card_title,
            "title_key": title,
            "desc_label": card_desc,
            "desc_key": desc
        })

        return card, layout_card

    def _language_combo_changed(self, text: str):
        lang_code = self.lang_map.get(text, "pt_BR")
        self.language_changed.emit(lang_code)

    def retranslate(self, lang_code: str):
        texts = languages.get(lang_code, languages["pt_BR"])

        self.label_title.setText(texts["settings_title"])

        for item in self.translatable_cards:
            title_text = texts.get(item["title_key"], "")
            desc_text = texts.get(item["desc_key"], "")

            item["title_label"].setText(title_text)
            item["desc_label"].setText(desc_text)

        self.btnDark.setText(texts["btn_dark"])
        self.btnLight.setText(texts["btn_light"])
        self.btnSystem.setText(texts["btn_system"])

        self.btnFast.setText(texts["btn_fast"])
        self.btnStandard.setText(texts["btn_standard"])
        self.btnDetailed.setText(texts["btn_detailed"])

        self.combo_language.blockSignals(True)
        if lang_code == "pt_BR":
            self.combo_language.setCurrentIndex(0)
        else:
            self.combo_language.setCurrentIndex(1)
        
        self.combo_language.setItemText(0, texts["language_ptbr"])
        self.combo_language.setItemText(1, texts["language_en"])
        self.combo_language.blockSignals(False)

        self.combo_data.setItemText(0, texts["data_op1"])
        self.combo_data.setItemText(1, texts["data_op2"])
        self.combo_data.setItemText(2, texts["data_op3"])

        self.btnComma.setText(texts["btn_comma"])
        self.btnPoint.setText(texts["btn_point"])
        self.btnBack.setText(texts["btn_back"])