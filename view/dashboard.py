import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class Dashboard(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()

    #Cria o conteudo da pagina
    self.setAttribute(QtCore.Qt.WA_StyledBackground, True) #Faz com que o QSS seja aplicado nessa subclasse
    self.setObjectName("conteudo")