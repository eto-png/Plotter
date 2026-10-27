import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

from config.locales import languages

class Loading(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()

    self.steps_labels = []

    #Cria o conteudo da pagina
    self.setAttribute(QtCore.Qt.WA_StyledBackground, True) #Faz com que o QSS seja aplicado nessa subclasse
    self.setObjectName("conteudo")

    layout_loading = QtWidgets.QVBoxLayout(self)
    layout_loading.setSpacing(0)
    layout_loading.addStretch()

    self.image_status = QtWidgets.QLabel()
    self.image_status.setObjectName("imgStatus")
    self.image_status.setScaledContents(True)
    self.set_status_image("chart")
    layout_loading.addWidget(self.image_status, alignment=QtCore.Qt.AlignCenter)

    self.label_title = QtWidgets.QLabel()
    self.label_title.setObjectName("loadingTitle")
    self.label_title.setAlignment(QtCore.Qt.AlignCenter)
    layout_loading.addWidget(self.label_title)

    self.progress_bar = QtWidgets.QProgressBar()
    self.progress_bar.setObjectName("progressBar")
    self.progress_bar.setFixedWidth(325)
    self.progress_bar.setFixedHeight(8)
    self.progress_bar.setTextVisible(False)
    self.progress_bar.setValue(0)
    layout_loading.addWidget(self.progress_bar, alignment=QtCore.Qt.AlignCenter)

    self.steps_container = QtWidgets.QVBoxLayout()
    self.steps_container.setSpacing(8)
    self.steps_container.setContentsMargins(0, 20, 0, 0)
    self.steps_container.setAlignment(QtCore.Qt.AlignCenter)
    layout_loading.addLayout(self.steps_container)

    layout_loading.addStretch()

  def set_status_image(self, state: str):
    self.image_status.setProperty("img", state)

    self.image_status.style().unpolish(self.image_status)
    self.image_status.style().polish(self.image_status)

  def setup_etapas(self, lista_etapas: list):
    for texto in lista_etapas:
      lbl = QtWidgets.QLabel(texto)
      lbl.setObjectName("stepLabel")
      self.steps_container.addWidget(lbl)
      self.steps_labels.append(lbl)

  def on_step_changed(self, step: int, percentage: int, message: str):
    self.progress_bar.setValue(percentage)

    for i in range(step + 1):
      lbl = self.steps_labels[i]
      font = lbl.font()
      if not font.strikeOut():
        font.setStrikeOut(True)
        lbl.setFont(font)

  def on_failed(self, index: int):
    self.set_status_image("error")

    self.retranslate(getattr(self, "current_lang", "pt_BR"))

    if 0 <= index < len(self.steps_labels):
      lbl_error = self.steps_labels[index]
      pb_error = self.progress_bar
      lbl_error.setStyleSheet("color: #FF5555")
      pb_error.setStyleSheet("#progressBar::chunk { background-color: #FF5555 }")

  def retranslate(self, lang_code: str):
    self.current_lang = lang_code

    texts = languages.get(lang_code, languages["pt_BR"])
    current_status = self.image_status.property("img")

    if current_status == "chart":
      self.label_title.setText(texts["loading_title"])
    else:
      self.label_title.setText(texts["loading_title_error"])