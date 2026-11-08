from PySide6 import QtCore, QtGui, QtWidgets

class Sidebar(QtWidgets.QFrame):
  animation_started = QtCore.Signal(bool)
  animation_finished = QtCore.Signal(bool)
  change_page = QtCore.Signal(int)

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setObjectName("sidebar")
    self.hide()

    layout = QtWidgets.QVBoxLayout(self)
    layout.setContentsMargins(12, 0, 12, 0)

    #Criação do layout para o cabeçalho do menu, permitindo que o botão de fechar fique na direita
    header_layout = QtWidgets.QHBoxLayout()
    header_layout.setContentsMargins(0, 10, 0, 0)

    #Criação do botão de fechar o menu lateral
    self.btnCloseSidebar = QtWidgets.QPushButton()
    self.btnCloseSidebar.setIcon(QtGui.QIcon())
    self.btnCloseSidebar.setObjectName("btnCloseSidebar")
    self.btnCloseSidebar.setFixedSize(30, 30)
    self.btnCloseSidebar.clicked.connect(self.toggle_menu)

    #Adicionando os elementos ao cabeçalho
    header_layout.addStretch()
    header_layout.addWidget(self.btnCloseSidebar)

    #Criação do botão "Outros dashboards"
    self.btnHistory = QtWidgets.QPushButton()
    self.btnHistory.setIcon(QtGui.QIcon())
    self.btnHistory.setIconSize(QtCore.QSize(23, 23))
    self.btnHistory.setObjectName("btnHistory")

    #Criação do botão "Configurações"
    self.btnConfig = QtWidgets.QPushButton()
    self.btnConfig.setIcon(QtGui.QIcon())
    self.btnConfig.setIconSize(QtCore.QSize(23, 23))
    self.btnConfig.setObjectName("btnConfig")
    self.btnConfig.clicked.connect(lambda: self.change_page.emit(1))

    #Criação da linha que separa as opções do menu lateral
    menuRow = QtWidgets.QWidget()
    menuRow.setFixedHeight(1)
    menuRow.setObjectName("menuRow")

    #Adicionando elementos ao menu lateral
    layout.addLayout(header_layout)
    layout.addWidget(self.btnHistory)
    layout.addWidget(menuRow)
    layout.addWidget(self.btnConfig)
    layout.addStretch()

  def toggle_menu(self):
    #Garante altura inteira útil
    if self.parent():
      self.setFixedHeight(self.parent().height() - 44)

    #Descobre o estado atual
    largura_atual = self.width()
    abrir = not self.isVisible() or largura_atual == 0

    largura_inicio, largura_fim = (0, 220) if abrir else (220, 0)

    # 1. EMITE O SINAL DE INÍCIO IMEDIATAMENTE (Esconde o btnMenu na main na hora!)
    self.animation_started.emit(abrir)

    if abrir:
      self.show()

    #Animação da Largura Mínima
    self.anim_min = QtCore.QPropertyAnimation(self, b"minimumWidth")
    self.anim_min.setDuration(250)
    self.anim_min.setStartValue(largura_inicio)
    self.anim_min.setEndValue(largura_fim)

    #Animação da Largura Máxima
    self.anim_max = QtCore.QPropertyAnimation(self, b"maximumWidth")
    self.anim_max.setDuration(250)
    self.anim_max.setStartValue(largura_inicio)
    self.anim_max.setEndValue(largura_fim)

    #Executa ambas ao mesmo tempo
    self.group = QtCore.QParallelAnimationGroup(self)
    self.group.addAnimation(self.anim_min)
    self.group.addAnimation(self.anim_max)

    def ao_terminar():
      if not abrir:
        self.hide()
      # 2. EMITE O SINAL DE FIM QUANDO A ANIMAÇÃO ACABA
      self.animation_finished.emit(abrir)

    # Conecta o término do grupo de animação
    self.group.finished.connect(ao_terminar)
    self.group.start()