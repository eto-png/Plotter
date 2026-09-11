import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

from view.home import Home

from config.paths import IMAGES_DIR, FONTS_DIR, STYLE_PATH

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #Esconde a barra de título e cria uma variavel pra armazenar a posição do mouse
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.old_pos = None

        #Cria o layout principal da janela
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        #Cria uma "div" para a barra de titulo
        self.title_bar = QtWidgets.QWidget()
        self.title_bar.setFixedHeight(44)
        self.title_bar.setObjectName("barraTitulo")

        #Cria o layout da barra de titulo
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 0, 0)

        #Elementos da barra de titulo
        self.title_label = QtWidgets.QLabel("Plotter")
        self.title_label.setObjectName("titulo")

        self.title_btnMin = QtWidgets.QPushButton()
        self.title_btnMin.setObjectName("btnMin")
        self.title_btnMin.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/window-minimize.svg"))
        self.title_btnMin.setFixedSize(44, 44)
        self.title_btnMin.clicked.connect(self.showMinimized)

        self.title_btnWid = QtWidgets.QPushButton()
        self.title_btnWid.setObjectName("btnWid")
        self.title_btnWid.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/cards.svg"))
        self.title_btnWid.setFixedSize(44, 44)
        self.title_btnWid.clicked.connect(self.change_size)

        self.title_btnClose = QtWidgets.QPushButton()
        self.title_btnClose.setObjectName("btnClose")
        self.title_btnClose.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/x.svg"))
        self.title_btnClose.setFixedSize(44, 44)
        self.title_btnClose.clicked.connect(self.close)

        #Adiciona os elementos ao layout da barra
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.title_btnMin)
        title_layout.addWidget(self.title_btnWid)
        title_layout.addWidget(self.title_btnClose)

        #Instancia a tela home
        self.homePage = Home()
        
        #Adiciona a barra e o conteudo ao layout principal
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.homePage)

        #Criação da "div" do menu lateral
        self.sidebar = QtWidgets.QFrame(self)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setGeometry(0, 44, 0, self.height() - 44)
        self.sidebar.hide()

        #Criação do layout do menu lateral
        layout_sidebar = QtWidgets.QVBoxLayout(self.sidebar)
        layout_sidebar.setContentsMargins(12, 0, 12, 0)

        #Criação do layout para o cabeçalho do menu, permitindo que o botão de fechar fique na direita
        layout_headerSidebar = QtWidgets.QHBoxLayout()
        layout_headerSidebar.setContentsMargins(0, 10, 0, 0)

        #Criação do botão de fechar o menu lateral
        self.btnCloseSidebar = QtWidgets.QPushButton()
        self.btnCloseSidebar.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/x.svg"))
        self.btnCloseSidebar.setObjectName("btnCloseSidebar")
        self.btnCloseSidebar.setFixedSize(30, 30)
        self.btnCloseSidebar.clicked.connect(self.toggle_menu)

        #Adicionando os elementos ao cabeçalho
        layout_headerSidebar.addStretch()
        layout_headerSidebar.addWidget(self.btnCloseSidebar)

        #Criação do botão "Outros dashboards"
        self.btnHistory = QtWidgets.QPushButton("Outros dashboards")
        self.btnHistory.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/dashboard.svg"))
        self.btnHistory.setIconSize(QtCore.QSize(23, 23))
        self.btnHistory.setObjectName("btnHistory")

        #Criação do botão "Configurações"
        self.btnConfig = QtWidgets.QPushButton("Configurações")
        self.btnConfig.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/settings.svg"))
        self.btnConfig.setIconSize(QtCore.QSize(23, 23))
        self.btnConfig.setObjectName("btnConfig")

        #Criação da linha que separa as opções do menu lateral
        menuRow = QtWidgets.QWidget()
        menuRow.setFixedHeight(1)
        menuRow.setObjectName("menuRow")

        #Adicionando elementos ao menu lateral
        layout_sidebar.addLayout(layout_headerSidebar)
        layout_sidebar.addWidget(self.btnHistory)
        layout_sidebar.addWidget(menuRow)
        layout_sidebar.addWidget(self.btnConfig)
        layout_sidebar.addStretch()

        #Criação do botão do menu lateral
        self.btnMenu = QtWidgets.QPushButton(self)
        self.btnMenu.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/menu-burger.svg"))
        self.btnMenu.setObjectName("btnMenu")
        self.btnMenu.setFixedSize(50, 45)
        self.btnMenu.move(10, 54)
        self.btnMenu.clicked.connect(self.toggle_menu)

        #Empurra o elemento pra camada mais alta, como o sidebar e o botão menu são elementos flutuantes (não estão em um layout), é necessario empurra-los para frente
        self.sidebar.raise_()
        self.btnMenu.raise_()

    #Função para recalcular e reajustar layouts, tamanho e posições de elemntos que não estão em um layout
    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"):
            self.sidebar.setFixedHeight(self.height() - 44)

    #Função para restaurar o tamanho da janela
    def change_size(self):
      if self.isMaximized():
        self.showNormal()
      else:
        self.showMaximized()

    #Funções para conseguir arrastar a tela
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            if self.title_bar.underMouse():
                self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.old_pos = None

    #Função para abrir o menu lateral
    def toggle_menu(self):
        # Garante altura inteira útil
        self.sidebar.setFixedHeight(self.height() - 44)

        #Descobre o estado atual
        largura_atual = self.sidebar.width()
        abrir = not self.sidebar.isVisible() or largura_atual == 0

        largura_inicio = 0 if abrir else 220
        largura_fim = 220 if abrir else 0

        if abrir:
            self.sidebar.show()
            self.btnMenu.hide()

        #Animação da Largura Mínima
        self.anim_min = QtCore.QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim_min.setDuration(250)
        self.anim_min.setStartValue(largura_inicio)
        self.anim_min.setEndValue(largura_fim)

        #Animação da Largura Máxima
        self.anim_max = QtCore.QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_max.setDuration(250)
        self.anim_max.setStartValue(largura_inicio)
        self.anim_max.setEndValue(largura_fim)

        #Executa ambas ao mesmo tempo
        self.group = QtCore.QParallelAnimationGroup(self)
        self.group.addAnimation(self.anim_min)
        self.group.addAnimation(self.anim_max)

        #Quando fecha, esconde a sidebar
        if not abrir:
            def ao_terminar():
                self.sidebar.hide()
                self.btnMenu.show()
                #Garante que o botão continue no topo e clicável
                self.btnMenu.raise_()

            self.group.finished.connect(ao_terminar)

        self.group.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtGui.QFontDatabase.addApplicationFont("fontes/Poppins-Regular.ttf")
    QtGui.QFontDatabase.addApplicationFont("fontes/Poppins-Bold.ttf")

    with open(STYLE_PATH, "r") as f:
        app.setStyleSheet(f.read())

    widget = Window()
    widget.resize(1000, 650)
    widget.show()

    sys.exit(app.exec())