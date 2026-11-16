from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QRectF, QSettings
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath

from view.components.colors import TemaEscuro, TemaClaro


class ItemMenuCustomizado(QWidget):
    toggled = Signal()

    def __init__(self, texto: str, tema, fonte: str, parent=None):
        super().__init__(parent)
        self.texto = texto
        self.tema = tema
        self.fonte = fonte
        self.marcado = True
        self._is_hovered = False

        self.setFixedHeight(32)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.marcado = not self.marcado
            self.update()
            self.toggled.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        if self._is_hovered:
            painter.setBrush(QBrush(self.tema.FUNDO_CARD))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)

        # Caixa de seleção (Checkbox)
        box_size = 16
        box_x = 12
        box_y = (rect.height() - box_size) / 2
        box_rect = QRectF(box_x, box_y, box_size, box_size)

        if self.marcado:
            painter.setBrush(QBrush(self.tema.DESTAQUE_PRINCIPAL))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(box_rect, 4, 4)

            pen_check = QPen(self.tema.FUNDO_CARD, 2)
            pen_check.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen_check.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen_check)
            painter.drawLine(box_x + 4, box_y + 8, box_x + 7, box_y + 11)
            painter.drawLine(box_x + 7, box_y + 11, box_x + 12, box_y + 4)
        else:
            painter.setBrush(QBrush(QColor("#4A4D59")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(box_rect, 4, 4)

        # Texto da opção
        painter.setFont(QFont(self.fonte, 10))
        painter.setPen(self.tema.TEXTO_PRINCIPAL)
        texto_rect = QRectF(box_x + 26, 0, rect.width() - 44, rect.height())
        painter.drawText(texto_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.texto)
        painter.end()


class MenuFlutuante(QWidget):
    def __init__(self, tema, parent=None):
        super().__init__(parent)
        self.tema = tema
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout_itens = QVBoxLayout(self)
        self.layout_itens.setContentsMargins(6, 6, 6, 6)
        self.layout_itens.setSpacing(2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(self.tema.FUNDO_PRINCIPAL))
        painter.setPen(QPen(QColor("#1E2338"), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.end()


class DropdownMenu(QWidget):
    selecao_alterada = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 36)
        self.settings = QSettings("TCC", "Plotter")
        self.tema = TemaEscuro() if self.settings.value("theme", "dark") == "dark" else TemaClaro()
        self.fonte = "Poppins"

        self.texto_exibido = "Todos"
        self._is_hovered = False

        self.popup = MenuFlutuante(self.tema, self)
        self.itens_criados = {}

    def adicionar_opcoes(self, lista_meses: list):
        for i in reversed(range(self.popup.layout_itens.count())):
            widget = self.popup.layout_itens.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.itens_criados.clear()

        for mes in lista_meses:
            item = ItemMenuCustomizado(mes, self.tema, self.fonte, self.popup)
            item.toggled.connect(self._avaliar_selecoes)
            self.popup.layout_itens.addWidget(item)
            self.itens_criados[mes] = item

    def _avaliar_selecoes(self):
        selecionados = [mes for mes, item in self.itens_criados.items() if item.marcado]
        total = len(self.itens_criados)

        if len(selecionados) == total or total == 0:
            self.texto_exibido = "Todos"
        elif len(selecionados) == 1:
            self.texto_exibido = selecionados[0]
        else:
            self.texto_exibido = f"{len(selecionados)} selecionados"

        self.update()
        self.selecao_alterada.emit(selecionados)

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToGlobal(self.rect().bottomLeft())
            self.popup.move(pos.x(), pos.y() + 4)
            self.popup.setFixedWidth(self.width())
            self.popup.show()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        btn_rect = QRectF(rect.adjusted(1, 1, -1, -1))
        raio = btn_rect.height() / 2  # Raio 18px (formato pílula)

        # Fundo do botão
        cor_fundo = self.tema.FUNDO_CARD.lighter(120) if self._is_hovered else self.tema.FUNDO_CARD
        painter.setBrush(QBrush(cor_fundo))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(btn_rect, raio, raio)

        # Texto alinhado à esquerda com 18px de margem interna
        painter.setFont(QFont(self.fonte, 10))
        painter.setPen(self.tema.TEXTO_PRINCIPAL)
        margem_esq = 18
        caixa_texto = QRectF(
            btn_rect.left() + margem_esq,
            btn_rect.top(),
            btn_rect.width() - margem_esq - 28,
            btn_rect.height()
        )
        painter.drawText(
            caixa_texto,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texto_exibido
        )

        # Seta (Chevron) à direita
        x_seta = btn_rect.right() - 18
        y_seta = btn_rect.center().y() - 2

        path_seta = QPainterPath()
        path_seta.moveTo(x_seta - 4, y_seta)
        path_seta.lineTo(x_seta, y_seta + 4)
        path_seta.lineTo(x_seta + 4, y_seta)

        pen_seta = QPen(self.tema.TEXTO_PRINCIPAL, 1.5)
        pen_seta.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_seta.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_seta)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_seta)

        painter.end()