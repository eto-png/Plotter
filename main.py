import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from view.home import Home

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
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("barraTitulo")

        #Cria o layout da barra de titulo
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)

        #Elementos da barra de titulo
        self.title_label = QtWidgets.QLabel("Plotter")
        self.title_label.setObjectName("titulo")

        self.title_btnMin = QtWidgets.QPushButton()
        self.title_btnMin.setObjectName("btnMin")
        self.title_btnMin.setIcon(QtGui.QIcon("images/window-minimize.svg"))
        self.title_btnMin.setFixedSize(30, 30)
        self.title_btnMin.clicked.connect(self.showMinimized)

        self.title_btnWei = QtWidgets.QPushButton()
        self.title_btnWei.setIcon(QtGui.QIcon("images/cards.svg"))
        self.title_btnWei.setFixedSize(30, 30)
        self.title_btnWei.clicked.connect(self.change_size)

        self.title_btnClose = QtWidgets.QPushButton()
        self.title_btnClose.setIcon(QtGui.QIcon("images/x.svg"))
        self.title_btnClose.setFixedSize(30, 30)
        self.title_btnClose.clicked.connect(self.close)

        #Adiciona os elementos ao layout da barra
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.title_btnMin)
        title_layout.addWidget(self.title_btnWei)
        title_layout.addWidget(self.title_btnClose)

        #Instancia a tela home
        self.homePage = Home()

        #Adiciona a barra e o conteudo ao layout principal
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.homePage)

    #Função para restaurar o tamanho da janela
    def change_size(self):
      if self.isMaximized():
        self.showNormal()
      else:
        self.showMaximized()

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

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtGui.QFontDatabase.addApplicationFont("fontes/Poppins-Regular.ttf")
    QtGui.QFontDatabase.addApplicationFont("fontes/Poppins-Bold.ttf")

    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())

    widget = Window()
    widget.resize(800, 500)
    widget.show()

    sys.exit(app.exec())