from PySide6 import QtCore, QtWidgets, QtGui
from config.paths import IMAGES_DIR, FONTS_DIR, STYLE_PATH

class Titlebar(QtWidgets.QFrame):
  def __init__(self, parent=None):
    super().__init__(parent)

    #Cria uma "div" para a barra de titulo
    self.setFixedHeight(44)
    self.setObjectName("barraTitulo")
    self.old_pos = None;
    
    #Cria o layout da barra de titulo
    title_layout = QtWidgets.QHBoxLayout(self)
    title_layout.setContentsMargins(15, 0, 0, 0)
    
    #Elementos da barra de titulo
    self.logo_label = QtWidgets.QLabel() #Criação da label para ter o logo
    self.logo_label.setObjectName("logo")
    pixmap_logo = QtGui.QPixmap(f"{IMAGES_DIR}/logo plotter.png")
    self.logo_label.setPixmap(pixmap_logo.scaled(35, 35, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
    
    self.title_label = QtWidgets.QLabel("Plotter") #Criação do "titulo"
    self.title_label.setObjectName("titulo")
    
    self.title_btnMin = QtWidgets.QPushButton() #Criação do botão de minimizar
    self.title_btnMin.setObjectName("btnMin")
    self.title_btnMin.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/window-minimize.svg"))
    self.title_btnMin.setFixedSize(44, 44)
    self.title_btnMin.clicked.connect(self.minimize)
    
    self.title_btnWid = QtWidgets.QPushButton() #Criação do botão de redimensionar
    self.title_btnWid.setObjectName("btnWid")
    self.title_btnWid.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/cards.svg"))
    self.title_btnWid.setFixedSize(44, 44)
    self.title_btnWid.clicked.connect(self.change_size)
    
    self.title_btnClose = QtWidgets.QPushButton() #Criação do botão de fechar
    self.title_btnClose.setObjectName("btnClose")
    self.title_btnClose.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/x.svg"))
    self.title_btnClose.setFixedSize(44, 44)
    self.title_btnClose.clicked.connect(self.close)
    
    #Adiciona os elementos ao layout da barra
    title_layout.addWidget(self.logo_label)
    title_layout.addWidget(self.title_label)
    title_layout.addStretch()
    title_layout.addWidget(self.title_btnMin)
    title_layout.addWidget(self.title_btnWid)
    title_layout.addWidget(self.title_btnClose)

    buttons = [self.title_btnMin, self.title_btnWid, self.title_btnClose]
    for btn in buttons:
      btn.setCursor(QtCore.Qt.PointingHandCursor)

  #Função para mudar o tamanho da janela
  def minimize(self):
    if self.window():
      self.window().showMinimized()

  def close(self):
    if self.window():
      self.window().close()

  def change_size(self):
    window = self.window()
    if window:
      if window.isMaximized():
        window.showNormal()
      else:
        window.showMaximized()

  #Funções para conseguir arrastar a tela
  def mousePressEvent(self, event: QtGui.QMouseEvent):
    if event.button() == QtCore.Qt.LeftButton:
      self.old_pos = event.globalPosition().toPoint()
  
  def mouseMoveEvent(self, event: QtGui.QMouseEvent):
    if self.old_pos is not None and self.window():
      delta = event.globalPosition().toPoint() - self.old_pos
      self.window().move(self.window().x() + delta.x(), self.window().y() + delta.y())
      self.old_pos = event.globalPosition().toPoint()
  
  def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
    self.old_pos = None