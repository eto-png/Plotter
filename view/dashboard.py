import json
from PySide6 import QtCore, QtWidgets

from config.paths import SCHEMA_DIR
from controller.dashboard_controller import DashboardController
from model.database.banco import BancoOperacoes
from model.services.dashboard_builder import DashboardBuilder


class Dashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Cria o conteudo da pagina
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)  # Faz com que o QSS seja aplicado nessa subclasse
        self.setObjectName("conteudo")

        self.banco: BancoOperacoes | None = None
        self.controller: DashboardController | None = None
        self.layout_data: dict | None = None

        layout_raiz = QtWidgets.QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QtWidgets.QGridLayout(self.container)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(16)
        for col in range(3):
            self.grid_layout.setColumnStretch(col, 1)

        self.scroll_area.setWidget(self.container)
        layout_raiz.addWidget(self.scroll_area)

    @staticmethod
    def _ler_perfil_schema(nome_dashboard: str) -> str:
        schema_path = SCHEMA_DIR / f"{nome_dashboard}_schema.json"
        if schema_path.exists():
            try:
                conteudo = schema_path.read_text(encoding="utf-8").strip()
                if conteudo:
                    dados = json.loads(conteudo)
                    perfil = dados.get("perfil_dashboard")
                    if isinstance(perfil, str) and perfil:
                        return perfil
            except (OSError, json.JSONDecodeError):
                pass
        return DashboardBuilder.FALLBACK_PERFIL

    def _limpar_grid(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            sub_layout = item.layout()
            if sub_layout is not None:
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget is not None:
                        sub_widget.setParent(None)
                        sub_widget.deleteLater()

    def carregar_dashboard(self, nome_dashboard: str) -> dict:
        perfil = self._ler_perfil_schema(nome_dashboard)
        self._limpar_grid()

        self.banco = BancoOperacoes(nome_dashboard)
        self.controller = DashboardController(self.banco)

        builder = DashboardBuilder(perfil, self.banco)
        self.layout_data = builder.construir(self.controller, parent_view=self.container)

        filtros = self.layout_data["filtros"]
        if filtros:
            filtros_layout = QtWidgets.QHBoxLayout()
            filtros_layout.setSpacing(16)
            for card_filtro in filtros:
                filtros_layout.addWidget(card_filtro)
            self.grid_layout.addLayout(filtros_layout, 0, 0, 1, 3)

        for item in self.layout_data["itens_grid"]:
            self.grid_layout.addWidget(
                item["widget"],
                item["row"],
                item["col"],
                item["rowspan"],
                item["colspan"],
            )

        self.controller.carregar_dashboard()
        return self.layout_data
