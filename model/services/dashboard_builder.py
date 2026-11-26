import json
from typing import Callable

from config.paths import DASHBOARD_MODELS_DIR
from controller.dashboard_controller import DashboardController
from model.database.banco import BancoOperacoes
from model.services.query_builder import QueryBuilder
from model.services.utilities import formatar_coluna_mes, formatar_moeda_brl
from view.components.charts import BarrasH, BarrasV, CardFiltro, CardKPI, LinhaDoTempo, Pizza


class DashboardBuilder:
    """
    Lê o template declarativo em `static/dashboard_models/<perfil>.json`,
    inspeciona o banco SQLite para resolver tabelas/colunas opcionais e fallbacks,
    instancia filtros, gráficos e QueryBuilders e os registra no DashboardController.
    """

    FALLBACK_PERFIL = "alto_giro"

    _MAPA_WIDGETS = {
        "CardKPI": CardKPI,
        "LinhaDoTempo": LinhaDoTempo,
        "BarrasH": BarrasH,
        "BarrasV": BarrasV,
        "Pizza": Pizza,
        "GraficoPizza": Pizza,
    }

    _QUERIES_DISPONIBILIDADE = {
        "vendedor": "SELECT COUNT(*) FROM vendedor",
        "localidade": "SELECT COUNT(*) FROM localidade",
        "categoria": "SELECT COUNT(*) FROM categoria",
        "produto.vl_custo": "SELECT COUNT(*) FROM produto WHERE vl_custo IS NOT NULL AND vl_custo > 0",
        "venda.vl_desconto": "SELECT COUNT(*) FROM venda WHERE vl_desconto IS NOT NULL AND vl_desconto > 0",
    }

    def __init__(self, perfil_id: str, banco: BancoOperacoes):
        self.perfil_id = perfil_id or self.FALLBACK_PERFIL
        self.banco = banco
        self.template = self._carregar_template(self.perfil_id)

    def _carregar_template(self, perfil_id: str) -> dict:
        caminho = DASHBOARD_MODELS_DIR / f"{perfil_id}.json"
        if not caminho.exists():
            print(
                f"[DashboardBuilder] Template '{perfil_id}.json' não encontrado. "
                f"Usando fallback '{self.FALLBACK_PERFIL}'."
            )
            self.perfil_id = self.FALLBACK_PERFIL
            caminho = DASHBOARD_MODELS_DIR / f"{self.FALLBACK_PERFIL}.json"

        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def _inspecionar_banco(self) -> dict[str, bool]:
        """Verifica quais tabelas/colunas opcionais possuem dados reais no .db."""
        disponibilidade: dict[str, bool] = {}
        self.banco.conectar()
        try:
            for chave, sql in self._QUERIES_DISPONIBILIDADE.items():
                try:
                    linhas = self.banco.executar_select(sql)
                    contagem = int(linhas[0][0]) if linhas and linhas[0] else 0
                    disponibilidade[chave] = contagem > 0
                except Exception:
                    disponibilidade[chave] = False
        finally:
            self.banco.desconectar()

        return disponibilidade

    def _resolver_widgets(self, disponibilidade: dict[str, bool]) -> list[dict]:
        """Ativa widgets principais disponíveis e substitui os indisponíveis por fallbacks."""
        widgets_ativos: list[dict] = []
        widgets_substituidos: set[str] = set()

        for widget_def in self.template.get("widgets", []):
            fallback_para = widget_def.get("fallback_para")
            requer = widget_def.get("requer_tabela")
            requisito_ok = requer is None or disponibilidade.get(requer, False)

            if fallback_para is None:
                if requisito_ok:
                    widgets_ativos.append(widget_def)
                else:
                    widgets_substituidos.add(widget_def["id"])
            elif fallback_para in widgets_substituidos:
                if requisito_ok:
                    widgets_ativos.append(widget_def)

        return widgets_ativos

    @staticmethod
    def _resolver_formatador(nome_formatador: str | None) -> Callable | None:
        if nome_formatador == "moeda":
            return formatar_moeda_brl
        if nome_formatador == "inteiro":
            return lambda v: f"{int(round(float(v or 0))):,}".replace(",", ".")
        if nome_formatador == "percentual":
            return lambda v: f"{float(v or 0):.1f}%".replace(".", ",")
        if nome_formatador == "ano_mes":
            return formatar_coluna_mes
        return None

    def construir(self, controller: DashboardController, parent_view=None) -> dict:
        """Constrói filtros e widgets em memória, registra no controller e retorna o grid."""
        disponibilidade = self._inspecionar_banco()

        filtros_instanciados: list[CardFiltro] = []
        for filtro_def in self.template.get("filtros", []):
            requer = filtro_def.get("requer_tabela")
            if requer is not None and not disponibilidade.get(requer, False):
                continue

            card_filtro = CardFiltro(
                parent=parent_view,
                titulo=filtro_def["titulo"],
                chave_filtro=filtro_def["chave"],
            )
            controller.registrar_filtro(card_filtro)
            filtros_instanciados.append(card_filtro)

        widgets_ativos = self._resolver_widgets(disponibilidade)
        itens_grid: list[dict] = []

        for widget_def in widgets_ativos:
            tipo = widget_def["tipo"]
            classe_widget = self._MAPA_WIDGETS.get(tipo)
            if classe_widget is None:
                raise ValueError(f"Tipo de widget desconhecido: '{tipo}'")

            widget = classe_widget(parent=parent_view, titulo=widget_def.get("titulo", ""))

            q_def = widget_def["query"]
            qb = QueryBuilder(
                query_base=q_def["query_base"],
                group_by=q_def.get("group_by") or "",
                order_by=q_def.get("order_by") or "",
                limit=q_def.get("limit"),
            )

            fn_formatador = self._resolver_formatador(widget_def.get("formatador"))
            controller.registrar_grafico(widget, qb, formatador=fn_formatador)

            grid = widget_def["grid"]
            itens_grid.append(
                {
                    "widget": widget,
                    "row": grid["row"],
                    "col": grid["col"],
                    "rowspan": grid.get("rowspan", 1),
                    "colspan": grid.get("colspan", 1),
                }
            )

        return {
            "perfil": self.perfil_id,
            "filtros": filtros_instanciados,
            "itens_grid": itens_grid,
        }
