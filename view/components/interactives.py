from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QRectF, QSettings
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QPalette

from view.components.colors import TemaEscuro, TemaClaro

class ItemMenuCustomizado(QWidget):
    """
    Item individual clicável dentro do menu suspenso, com checkbox e texto
    desenhados manualmente via QPainter.
    """
    toggled = Signal()

    def __init__(self, texto: str, tema, fonte: str, negrito: bool = False, parent=None):
        super().__init__(parent)
        self.texto = texto
        self.tema = tema
        self.fonte = fonte
        self.negrito = negrito
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
        peso = QFont.Weight.Bold if self.negrito else QFont.Weight.Normal
        painter.setFont(QFont(self.fonte, 10, peso))
        painter.setPen(self.tema.TEXTO_PRINCIPAL)
        texto_rect = QRectF(box_x + 26, 0, rect.width() - 44, rect.height())
        painter.drawText(
            texto_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texto
        )
        painter.end()

class MenuFlutuante(QWidget):
    """
    Popup flutuante sem bordas nativas do SO, com fundo sólido pintado via
    QPainter e rolagem via mouse wheel sem barra nativa cinza.
    """
    def __init__(self, tema, max_altura: int = 260, parent=None):
        super().__init__(parent)
        self.tema = tema
        self.max_altura = max_altura

        # WA_TranslucentBackground APENAS na janela popup raiz (para os cantos arredondados)
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(6, 6, 6, 6)
        layout_externo.setSpacing(0)

        paleta_transparente = QPalette()
        paleta_transparente.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.transparent)
        paleta_transparente.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setAutoFillBackground(False)
        self.scroll_area.setPalette(paleta_transparente)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.viewport().setPalette(paleta_transparente)

        self.container_itens = QWidget()
        self.container_itens.setAutoFillBackground(False)
        self.container_itens.setPalette(paleta_transparente)

        self.layout_itens = QVBoxLayout(self.container_itens)
        self.layout_itens.setContentsMargins(0, 0, 0, 0)
        self.layout_itens.setSpacing(2)

        self.scroll_area.setWidget(self.container_itens)
        layout_externo.addWidget(self.scroll_area)

    def ajustar_altura(self, qtd_itens: int):
        """Calcula a altura ideal do popup com base na quantidade de itens."""
        altura_conteudo = (qtd_itens * 34) + 14
        self.setFixedHeight(min(max(altura_conteudo, 46), self.max_altura))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(self.tema.FUNDO_PRINCIPAL))
        painter.setPen(QPen(QColor("#1E2338"), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)
        painter.end()
class DropdownMenu(QWidget):
    """
    Botão em pílula com seleção múltipla, opção 'Selecionar Todos'
    e memória de itens desmarcados para filtros cascateados sem perda de opções.
    """
    selecao_alterada = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 36)
        self.settings = QSettings("TCC", "Plotter")
        self.tema = TemaEscuro() if self.settings.value("theme", "dark") == "dark" else TemaClaro()
        self.fonte = "Poppins"

        self.texto_exibido = "Todos"
        self._is_hovered = False

        self.popup = MenuFlutuante(self.tema, parent=self)
        self.item_selecionar_todos: ItemMenuCustomizado | None = None
        self.itens_criados: dict[str, ItemMenuCustomizado] = {}
        self.desmarcados: set[str] = set()

    def adicionar_opcoes(
        self,
        lista_opcoes: list[str],
        manter_selecao: list[str] | None = None,
        resetar_selecao: bool = False
    ):
        """
        Popula ou atualiza as opções do dropdown preservando exatamente
        o que o usuário desmarcou antes do cascateamento.
        """
        if resetar_selecao:
            self.desmarcados.clear()

        for i in reversed(range(self.popup.layout_itens.count())):
            widget = self.popup.layout_itens.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.itens_criados.clear()
        self.item_selecionar_todos = None

        if lista_opcoes:
            self.item_selecionar_todos = ItemMenuCustomizado(
                "Selecionar Todos", self.tema, self.fonte, negrito=True, parent=self.popup
            )
            self.item_selecionar_todos.toggled.connect(self._ao_alternar_todos)
            self.popup.layout_itens.addWidget(self.item_selecionar_todos)

        for opcao in lista_opcoes:
            item = ItemMenuCustomizado(opcao, self.tema, self.fonte, parent=self.popup)
            item.marcado = opcao not in self.desmarcados
            item.toggled.connect(lambda it=item: self._ao_alternar_item(it))
            self.popup.layout_itens.addWidget(item)
            self.itens_criados[opcao] = item

        total_visuais = len(lista_opcoes) + (1 if self.item_selecionar_todos else 0)
        self.popup.ajustar_altura(total_visuais)
        self._atualizar_rotulo()

    def obter_selecionados(self) -> list[str] | None:
        """
        Retorna:
        - None: quando todas as opções visíveis estão marcadas ('Todos') ou o menu está vazio.
        - list[str]: subconjunto marcado (ou [] se o usuário desmarcou tudo).
        """
        if not self.itens_criados:
            return None

        marcados = [opcao for opcao, item in self.itens_criados.items() if item.marcado]
        if len(marcados) == len(self.itens_criados):
            return None

        return marcados

    def obter_todas_opcoes(self) -> list[str]:
        """Retorna todas as opções disponíveis no dropdown, independente da seleção."""
        return list(self.itens_criados.keys())

    def _ao_alternar_item(self, item: ItemMenuCustomizado):
        if item.marcado:
            self.desmarcados.discard(item.texto)
        else:
            self.desmarcados.add(item.texto)

        self._avaliar_selecoes()

    def _ao_alternar_todos(self):
        """Marca ou desmarca todos os itens de uma vez e emite uma única atualização."""
        if not self.item_selecionar_todos:
            return

        novo_estado = self.item_selecionar_todos.marcado
        if novo_estado:
            self.desmarcados.clear()
        else:
            self.desmarcados.update(self.itens_criados.keys())

        for item in self.itens_criados.values():
            item.marcado = novo_estado
            item.update()

        self._avaliar_selecoes()

    def _atualizar_rotulo(self) -> list[str] | None:
        """Atualiza o texto do botão e o estado visual do checkbox 'Selecionar Todos'."""
        total = len(self.itens_criados)
        qtd_marcados = sum(1 for item in self.itens_criados.values() if item.marcado)

        if self.item_selecionar_todos:
            todos_marcados = (total > 0 and qtd_marcados == total)
            if self.item_selecionar_todos.marcado != todos_marcados:
                self.item_selecionar_todos.marcado = todos_marcados
                self.item_selecionar_todos.update()

        if qtd_marcados == total and total > 0:
            self.texto_exibido = "Todos"
        elif total == 0 or qtd_marcados == 0:
            self.texto_exibido = "Nenhum"
        elif qtd_marcados == 1:
            unico = next(op for op, item in self.itens_criados.items() if item.marcado)
            self.texto_exibido = unico
        else:
            self.texto_exibido = f"{qtd_marcados} selecionados"

        self.update()
        return self.obter_selecionados()

    def _avaliar_selecoes(self):
        selecionados = self._atualizar_rotulo()
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
        if event.button() == Qt.MouseButton.LeftButton and self.itens_criados:
            pos = self.mapToGlobal(self.rect().bottomLeft())
            self.popup.move(pos.x(), pos.y() + 4)
            self.popup.setFixedWidth(max(self.width(), 195))
            self.popup.show()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        btn_rect = QRectF(rect.adjusted(1, 1, -1, -1))
        raio = btn_rect.height() / 2

        cor_fundo = self.tema.FUNDO_CARD.lighter(120) if self._is_hovered else self.tema.FUNDO_CARD
        painter.setBrush(QBrush(cor_fundo))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(btn_rect, raio, raio)

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

class DropdownMenu(QWidget):
    """
    Botão em pílula com seleção múltipla, opção 'Selecionar Todos'
    e memória de itens desmarcados para filtros cascateados sem perda de opções.
    """
    selecao_alterada = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 36)
        self.settings = QSettings("TCC", "Plotter")
        self.tema = TemaEscuro() if self.settings.value("theme", "dark") == "dark" else TemaClaro()
        self.fonte = "Poppins"

        self.texto_exibido = "Todos"
        self._is_hovered = False

        self.popup = MenuFlutuante(self.tema, parent=self)
        self.item_selecionar_todos: ItemMenuCustomizado | None = None
        self.itens_criados: dict[str, ItemMenuCustomizado] = {}
        self.desmarcados: set[str] = set()

    def adicionar_opcoes(
        self,
        lista_opcoes: list[str],
        manter_selecao: list[str] | None = None,
        resetar_selecao: bool = False
    ):
        """
        Popula ou atualiza as opções do dropdown preservando exatamente
        o que o usuário desmarcou antes do cascateamento.
        """
        if resetar_selecao:
            self.desmarcados.clear()

        for i in reversed(range(self.popup.layout_itens.count())):
            widget = self.popup.layout_itens.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.itens_criados.clear()
        self.item_selecionar_todos = None

        if lista_opcoes:
            self.item_selecionar_todos = ItemMenuCustomizado(
                "Selecionar Todos", self.tema, self.fonte, negrito=True, parent=self.popup
            )
            self.item_selecionar_todos.toggled.connect(self._ao_alternar_todos)
            self.popup.layout_itens.addWidget(self.item_selecionar_todos)

        for opcao in lista_opcoes:
            item = ItemMenuCustomizado(opcao, self.tema, self.fonte, parent=self.popup)
            item.marcado = opcao not in self.desmarcados
            item.toggled.connect(lambda it=item: self._ao_alternar_item(it))
            self.popup.layout_itens.addWidget(item)
            self.itens_criados[opcao] = item

        total_visuais = len(lista_opcoes) + (1 if self.item_selecionar_todos else 0)
        self.popup.ajustar_altura(total_visuais)
        self._atualizar_rotulo()

    def obter_selecionados(self) -> list[str] | None:
        """
        Retorna:
        - None: quando todas as opções visíveis estão marcadas ('Todos') ou o menu está vazio.
        - list[str]: subconjunto marcado (ou [] se o usuário desmarcou tudo).
        """
        if not self.itens_criados:
            return None

        marcados = [opcao for opcao, item in self.itens_criados.items() if item.marcado]
        if len(marcados) == len(self.itens_criados):
            return None

        return marcados

    def obter_todas_opcoes(self) -> list[str]:
        """Retorna todas as opções disponíveis no dropdown, independente da seleção."""
        return list(self.itens_criados.keys())

    def definir_selecao(self, valores: list[str] | None) -> None:
        """Define a seleção do dropdown programaticamente (usado pela IA)."""
        if valores is None:
            self.desmarcados.clear()
        else:
            selecionados = set(valores)
            self.desmarcados = {
                op for op in self.itens_criados.keys() if op not in selecionados
            }

        for opcao, item in self.itens_criados.items():
            item.marcado = opcao not in self.desmarcados
            item.update()

        self._atualizar_rotulo()

    def _ao_alternar_item(self, item: ItemMenuCustomizado):
        if item.marcado:
            self.desmarcados.discard(item.texto)
        else:
            self.desmarcados.add(item.texto)

        self._avaliar_selecoes()

    def _ao_alternar_todos(self):
        """Marca ou desmarca todos os itens de uma vez e emite uma única atualização."""
        if not self.item_selecionar_todos:
            return

        novo_estado = self.item_selecionar_todos.marcado
        if novo_estado:
            self.desmarcados.clear()
        else:
            self.desmarcados.update(self.itens_criados.keys())

        for item in self.itens_criados.values():
            item.marcado = novo_estado
            item.update()

        self._avaliar_selecoes()

    def _atualizar_rotulo(self) -> list[str] | None:
        """Atualiza o texto do botão e o estado visual do checkbox 'Selecionar Todos'."""
        total = len(self.itens_criados)
        qtd_marcados = sum(1 for item in self.itens_criados.values() if item.marcado)

        if self.item_selecionar_todos:
            todos_marcados = (total > 0 and qtd_marcados == total)
            if self.item_selecionar_todos.marcado != todos_marcados:
                self.item_selecionar_todos.marcado = todos_marcados
                self.item_selecionar_todos.update()

        if qtd_marcados == total and total > 0:
            self.texto_exibido = "Todos"
        elif total == 0 or qtd_marcados == 0:
            self.texto_exibido = "Nenhum"
        elif qtd_marcados == 1:
            unico = next(op for op, item in self.itens_criados.items() if item.marcado)
            self.texto_exibido = unico
        else:
            self.texto_exibido = f"{qtd_marcados} selecionados"

        self.update()
        return self.obter_selecionados()

    def _avaliar_selecoes(self):
        selecionados = self._atualizar_rotulo()
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
        if event.button() == Qt.MouseButton.LeftButton and self.itens_criados:
            pos = self.mapToGlobal(self.rect().bottomLeft())
            self.popup.move(pos.x(), pos.y() + 4)
            self.popup.setFixedWidth(max(self.width(), 195))
            self.popup.show()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        btn_rect = QRectF(rect.adjusted(1, 1, -1, -1))
        raio = btn_rect.height() / 2

        cor_fundo = self.tema.FUNDO_CARD.lighter(120) if self._is_hovered else self.tema.FUNDO_CARD
        painter.setBrush(QBrush(cor_fundo))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(btn_rect, raio, raio)

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