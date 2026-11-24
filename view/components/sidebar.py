from config.paths import FONTS_DIR, IMAGES_DIR, STYLE_PATH
from PySide6 import QtCore, QtGui, QtWidgets
from config.locales import languages

class Sidebar(QtWidgets.QFrame):
  animation_started = QtCore.Signal(bool)
  animation_finished = QtCore.Signal(bool)
  change_page = QtCore.Signal(int)
  ai_prompt = QtCore.Signal(str)

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setObjectName("sidebar")
    self.is_fixed = False

    self.main_layout = QtWidgets.QVBoxLayout(self)
    self.main_layout.setContentsMargins(12, 0, 12, 0)

    self.stack = QtWidgets.QStackedWidget()
    self.main_layout.addWidget(self.stack)

    # 1. Cria e adiciona as duas views no stack
    self.home_view = self.create_home_view()
    self.dashboard_view = self.create_dashboard_view()

    self.stack.addWidget(self.home_view)  # Índice 0
    self.stack.addWidget(self.dashboard_view)  # Índice 1

  def create_home_view(self) -> QtWidgets.QWidget:
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    layout.setContentsMargins(0, 10, 0, 0)

    # Cabeçalho com botão de fechar
    header_layout = QtWidgets.QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 0)

    self.btnCloseSidebar = QtWidgets.QPushButton()
    self.btnCloseSidebar.setIcon(QtGui.QIcon())
    self.btnCloseSidebar.setObjectName("btnCloseSidebar")
    self.btnCloseSidebar.setFixedSize(30, 30)
    self.btnCloseSidebar.clicked.connect(self.toggle_menu)

    header_layout.addStretch()
    header_layout.addWidget(self.btnCloseSidebar)

    # Título "Outros dashboards"
    history_title, self.lblHistory = self.create_title("history")

    # Botão "Configurações" da Home
    self.btnHomeConfig = QtWidgets.QPushButton()
    self.btnHomeConfig.setIcon(QtGui.QIcon())
    self.btnHomeConfig.setIconSize(QtCore.QSize(23, 23))
    self.btnHomeConfig.setObjectName("btnConfig")
    self.btnHomeConfig.clicked.connect(lambda: self.change_page.emit(1))
    self.btnHomeConfig.setCursor(QtCore.Qt.PointingHandCursor)

    # Montagem do layout
    layout.addLayout(header_layout)
    layout.addLayout(history_title)  # <- Corrigido (addLayout)
    layout.addWidget(self.create_divider())  # <- Linha criada pela função
    layout.addWidget(self.btnHomeConfig)
    layout.addStretch()

    return widget

  def create_dashboard_view(self) -> QtWidgets.QWidget:
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    layout.setContentsMargins(0, 10, 0, 0)

    #Botão "Novo Dashboard"
    self.btnNewDash = QtWidgets.QPushButton()
    self.btnNewDash.setObjectName("btnNewDash")
    self.btnNewDash.setIcon(QtGui.QIcon())
    self.btnNewDash.setCursor(QtCore.Qt.PointingHandCursor)

    #Categoria "Dashboards"
    dash_title, self.lblDash = self.create_title("dash")

    self.scroll = QtWidgets.QScrollArea()
    self.scroll.setWidgetResizable(True)
    self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    self.scroll.setMaximumHeight(150)
    self.scroll.setObjectName("scroll")

    self.scroll_content = QtWidgets.QWidget()
    self.scroll_content.setObjectName("scroll_content")
    self.dash_list = QtWidgets.QVBoxLayout(self.scroll_content)
    self.dash_list.setContentsMargins(0, 0, 0, 0)

    for name in ["Bolo du Bom", "Joalheria Jóia", "Padoca do Pedroca"]:
      btn_item = QtWidgets.QPushButton(name)
      btn_item.setCursor(QtCore.Qt.PointingHandCursor)
      btn_item.setObjectName("btnDashItem")
      self.dash_list.addWidget(btn_item)

    self.dash_list.addStretch()
    self.scroll.setWidget(self.scroll_content)

    #Categoria "Dados desse Dashboard"
    data_title, self.lblData = self.create_title("data")

    #Categoria "Exportar"
    export_title, self.lblExport = self.create_title("export")
    self.btnPDF = QtWidgets.QPushButton()
    #Botões de exportar
    self.btnPDF.setObjectName("btnPDF")
    self.btnPDF.setCursor(QtCore.Qt.PointingHandCursor)
    self.btnJPG = QtWidgets.QPushButton()
    self.btnJPG.setObjectName("btnJPG")
    self.btnJPG.setCursor(QtCore.Qt.PointingHandCursor)

    #Botão "Configurações"
    self.btnDashConfig = QtWidgets.QPushButton()
    self.btnDashConfig.setIcon(QtGui.QIcon())
    self.btnDashConfig.setIconSize(QtCore.QSize(23, 23))
    self.btnDashConfig.setObjectName("btnConfig")
    self.btnDashConfig.clicked.connect(lambda: self.change_page.emit(1))
    self.btnDashConfig.setCursor(QtCore.Qt.PointingHandCursor)

    self.ai_container = QtWidgets.QFrame()
    self.ai_container.setObjectName("aiContainer")
    self.ai_container.setFixedHeight(38)

    ai_layout = QtWidgets.QHBoxLayout(self.ai_container)
    ai_layout.setContentsMargins(0, 0, 0, 0)
    ai_layout.setSpacing(0)

    #Campo de texto
    self.inputAI = QtWidgets.QLineEdit()
    self.inputAI.setObjectName("inputAI")
    self.inputAI.setPlaceholderText("Peça um filtro para a I.A.")
    self.inputAI.returnPressed.connect(self.send_ai_prompt)

    #Botão de enviar
    self.btnSendAI = QtWidgets.QPushButton()
    self.btnSendAI.setObjectName("btnSendAI")
    self.btnSendAI.setFixedSize(27, 27)
    self.btnSendAI.setCursor(QtCore.Qt.PointingHandCursor)
    self.btnSendAI.clicked.connect(self.send_ai_prompt)

    ai_layout.addWidget(self.inputAI)
    ai_layout.addWidget(self.btnSendAI)

    #Montagem do layout
    layout.addWidget(self.btnNewDash)
    layout.addWidget(self.create_divider())
    layout.addLayout(dash_title)
    layout.addWidget(self.scroll)  # <- Corrigido (adiciona o self.scroll)
    layout.addWidget(self.create_divider())
    layout.addLayout(data_title)
    layout.addWidget(self.create_divider())
    layout.addLayout(export_title)
    layout.addWidget(self.btnPDF)
    layout.addWidget(self.btnJPG)
    layout.addWidget(self.create_divider())
    layout.addWidget(self.btnDashConfig)
    layout.addStretch()
    layout.addWidget(self.ai_container)  # <-- Caixa da IA
    layout.addWidget(self.create_divider())
    #layout.addStretch()

    return widget

  #Função auxiliar para criar linhas divisórias sem repetir código
  def create_divider(self) -> QtWidgets.QWidget:
    line = QtWidgets.QWidget()
    line.setFixedHeight(1)
    line.setObjectName("menuRow")
    return line

  #Função auxiliar para criar os títulos utilizados na sidebar
  def create_title(self, name: str) -> tuple[QtWidgets.QHBoxLayout, QtWidgets.QLabel]:
    title_layout = QtWidgets.QHBoxLayout()
    title_layout.setSpacing(5)

    lbl_icon = QtWidgets.QLabel()
    lbl_icon.setObjectName(f"sbOptIcon_{name}")
    lbl_icon.setFixedSize(23, 23)
    lbl_icon.setScaledContents(True)

    lbl_title = QtWidgets.QLabel()
    lbl_title.setObjectName("sbOptTitle")

    title_layout.addWidget(lbl_icon)
    title_layout.addWidget(lbl_title)
    title_layout.addStretch()

    return title_layout, lbl_title

  def set_mode(self, mode: str):
    self.setProperty("mode", mode)

    if mode == "home":
      self.is_fixed = False
      self.stack.setCurrentIndex(0)
      self.setMinimumWidth(0)
      self.setMaximumWidth(0)
      self.hide()
    elif mode == "dashboard":
      self.is_fixed = True
      self.stack.setCurrentIndex(1)
      self.setFixedWidth(225)
      self.show()

    self.style().unpolish(self)
    self.style().polish(self)

    for child in self.findChildren(QtWidgets.QWidget):
      child.setProperty("mode", mode)
      child.style().unpolish(child)
      child.style().polish(child)

    self.repaint()

  def send_ai_prompt(self):
    texto = self.inputAI.text().strip()
    if texto:
      self.ai_prompt.emit(texto)
      self.inputAI.clear()

  def retranslate(self, lang_code: str):
    texts = languages.get(lang_code, languages["pt_BR"])

    self.lblHistory.setText(texts["menu_dashboard"])
    self.btnHomeConfig.setText(texts["menu_settings"])

    self.btnNewDash.setText(texts["menu_newdash"])
    self.lblDash.setText(texts["menu_dashboard"])
    self.lblData.setText(texts["menu_datadash"])
    self.lblExport.setText(texts["menu_export"])
    self.btnPDF.setText(texts["menu_pdf"])
    self.btnJPG.setText(texts["menu_jpg"])
    self.btnDashConfig.setText(texts["menu_settings"])

  def toggle_menu(self):
    if self.is_fixed:
      return

    if self.parent():
      self.setFixedHeight(self.parent().height() - 44)

    largura_atual = self.width()
    abrir = not self.isVisible() or largura_atual == 0
    largura_inicio, largura_fim = (0, 225) if abrir else (225, 0)

    self.animation_started.emit(abrir)

    if abrir:
      self.show()

    self.anim_min = QtCore.QPropertyAnimation(self, b"minimumWidth")
    self.anim_min.setDuration(250)
    self.anim_min.setStartValue(largura_inicio)
    self.anim_min.setEndValue(largura_fim)

    self.anim_max = QtCore.QPropertyAnimation(self, b"maximumWidth")
    self.anim_max.setDuration(250)
    self.anim_max.setStartValue(largura_inicio)
    self.anim_max.setEndValue(largura_fim)

    self.group = QtCore.QParallelAnimationGroup(self)
    self.group.addAnimation(self.anim_min)
    self.group.addAnimation(self.anim_max)

    def ao_terminar():
      if not abrir:
        self.hide()
      self.animation_finished.emit(abrir)

    self.group.finished.connect(ao_terminar)
    self.group.start()