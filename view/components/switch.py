from PySide6 import QtCore, QtWidgets, QtGui

class SwitchToggle(QtWidgets.QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedSize(120, 30)  #Espaço para o switch + texto "Ativo"

        #Animação do deslocamento da bolinha branca
        self._circle_position = 3  #Posição inicial (desligado)
        self.anim = QtCore.QPropertyAnimation(self, b"circle_position", self)
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.stateChanged.connect(self.start_transition)

    #Propriedade do Qt que permite que a animação altere a posição x da bolinha
    @QtCore.Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()  #Redesenhar a tela a cada frame

    def start_transition(self, state):
        self.anim.stop()
        end_pos = 25 if state else 3
        self.anim.setStartValue(self._circle_position)
        self.anim.setEndValue(end_pos)
        self.anim.start()

    #Redesenha o controle visualmente usando QPainter
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        #Definição de cores
        bg_color = (
            QtGui.QColor("#62F59F") if self.isChecked() else QtGui.QColor("#2A313D")
        )
        border_color = (
            QtGui.QColor("#62F59F") if self.isChecked() else QtGui.QColor("#455060")
        )
        text_color = (
            QtGui.QColor("#62F59F") if self.isChecked() else QtGui.QColor("#8A99AD")
        )

        #Desenha o fundo da pílula
        painter.setPen(QtGui.QPen(border_color, 1))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(0, 3, 50, 24, 12, 12)

        #Desenha a bolinha branca
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor("#FFFFFF"))
        painter.drawEllipse(QtCore.QPointF(self._circle_position + 12, 15), 9, 9)

        #Desenha o texto ao lado
        painter.setPen(text_color)
        font = self.font()
        font.setPixelSize(13)
        font.setWeight(QtGui.QFont.Medium)
        painter.setFont(font)

        texto = "Ativo" if self.isChecked() else "Inativo"
        painter.drawText(
            QtCore.QRect(60, 0, 60, 30), QtCore.Qt.AlignVCenter, texto
        )

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            #Pega a posição X de onde aconteceu o clique do mouse
            click_x = event.position().x()

          #Como a pilula tem 50px de largura, só altera o estado se o clique for dentro de 0 a 50px
            if 0 <= click_x <= 50:
                self.setChecked(not self.isChecked())
                event.accept()
            else:
                #Se clicar no texto, ignora o clique
                event.ignore()
        else:
          super().mousePressEvent(event)
