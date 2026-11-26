from typing import Callable

from model.database.banco import BancoOperacoes
from model.services.query_builder import QueryBuilder
from model.services.utilities import formatar_coluna_mes, formatar_iso_para_mes
from view.components.charts import CardFiltro, CardKPI


class DashboardController:
    """
    Controlador responsável por gerenciar filtros cascateados e atualizar
    todos os widgets registrados a partir de seus respectivos QueryBuilders.
    """

    _QUERIES_FILTRO_PADRAO = {
        "mes": {
            "query_base": (
                "SELECT strftime('%Y-%m', v.dt_venda) AS ym "
                "FROM venda v "
                "JOIN lista_produtos lp ON v.cd_venda = lp.cd_venda "
                "JOIN produto p ON lp.cd_produto = p.cd_produto"
            ),
            "group_by": "ym",
            "order_by": "ym ASC",
        },
        "categoria": {
            "query_base": (
                "SELECT DISTINCT c.nm_categoria "
                "FROM venda v "
                "JOIN lista_produtos lp ON v.cd_venda = lp.cd_venda "
                "JOIN produto p ON lp.cd_produto = p.cd_produto "
                "JOIN lista_categoria lc ON p.cd_produto = lc.cd_produto "
                "JOIN categoria c ON lc.cd_categoria = c.cd_categoria"
            ),
            "group_by": "",
            "order_by": "c.nm_categoria ASC",
        },
        "produto": {
            "query_base": (
                "SELECT DISTINCT p.nm_produto "
                "FROM venda v "
                "JOIN lista_produtos lp ON v.cd_venda = lp.cd_venda "
                "JOIN produto p ON lp.cd_produto = p.cd_produto"
            ),
            "group_by": "",
            "order_by": "p.nm_produto ASC",
        },
        "vendedor": {
            "query_base": (
                "SELECT DISTINCT vend.nm_vendedor "
                "FROM venda v "
                "JOIN vendedor vend ON v.cd_vendedor = vend.cd_vendedor "
                "JOIN lista_produtos lp ON v.cd_venda = lp.cd_venda "
                "JOIN produto p ON lp.cd_produto = p.cd_produto"
            ),
            "group_by": "",
            "order_by": "vend.nm_vendedor ASC",
        },
        "localidade": {
            "query_base": (
                "SELECT DISTINCT loc.nm_localidade "
                "FROM venda v "
                "JOIN localidade loc ON v.cd_localidade = loc.cd_localidade "
                "JOIN lista_produtos lp ON v.cd_venda = lp.cd_venda "
                "JOIN produto p ON lp.cd_produto = p.cd_produto"
            ),
            "group_by": "",
            "order_by": "loc.nm_localidade ASC",
        },
    }

    def __init__(self, banco: BancoOperacoes):
        self.banco = banco
        self._filtros: dict[str, tuple[CardFiltro, QueryBuilder]] = {}
        self._graficos: list[tuple[object, QueryBuilder, Callable | None]] = []

    def _criar_qb_filtro_padrao(self, chave: str) -> QueryBuilder:
        cfg = self._QUERIES_FILTRO_PADRAO.get(chave)
        if not cfg:
            raise ValueError(f"Chave de filtro não suportada: '{chave}'")
        return QueryBuilder(
            query_base=cfg["query_base"],
            group_by=cfg["group_by"],
            order_by=cfg["order_by"],
        )

    def registrar_filtro(
        self,
        card_filtro: CardFiltro,
        qb_opcoes: QueryBuilder | None = None,
    ) -> None:
        chave = card_filtro.chave_filtro
        qb = qb_opcoes or self._criar_qb_filtro_padrao(chave)
        self._filtros[chave] = (card_filtro, qb)
        card_filtro.conectar_acao_filtro(self.atualizar_por_filtros)

    def registrar_grafico(
        self,
        widget,
        qb: QueryBuilder,
        formatador: Callable | None = None,
    ) -> None:
        self._graficos.append((widget, qb, formatador))

    def _obter_estado_filtros(self) -> dict[str, list[str]]:
        return {
            chave: card_filtro.obter_selecionados()
            for chave, (card_filtro, _) in self._filtros.items()
        }

    def _extrair_opcoes_filtro(self, chave: str, linhas: list) -> list[str]:
        opcoes = []
        for row in linhas:
            valor = row[0] if isinstance(row, (tuple, list)) else row
            if valor is None:
                continue
            if chave == "mes":
                opcoes.append(formatar_iso_para_mes(str(valor)))
            else:
                opcoes.append(str(valor))
        return opcoes

    def carregar_dashboard(self) -> None:
        """Popula todos os filtros com opções iniciais e renderiza todos os widgets."""
        self.banco.conectar()
        try:
            for chave, (card_filtro, qb) in self._filtros.items():
                qb.limpar_filtros()
                sql, params = qb.construir()
                linhas = self.banco.executar_select(sql, params)
                opcoes = self._extrair_opcoes_filtro(chave, linhas)
                card_filtro.popular_filtro(opcoes)

            estado_atual = self._obter_estado_filtros()
            self._atualizar_graficos(estado_atual)
        finally:
            self.banco.desconectar()

    def atualizar_por_filtros(self, _selecao_disparadora=None) -> None:
        """Executa o cascateamento entre filtros e atualiza os gráficos sincronizados."""
        estado_atual = self._obter_estado_filtros()

        self.banco.conectar()
        try:
            for chave, (card_filtro, qb) in self._filtros.items():
                sql_f, params_f = qb.aplicar_filtros_dashboard(
                    estado_atual, ignorar=chave, modo_opcoes=True
                ).construir()
                linhas_f = self.banco.executar_select(sql_f, params_f)
                opcoes = self._extrair_opcoes_filtro(chave, linhas_f)
                card_filtro.popular_filtro(opcoes, manter_selecao=estado_atual.get(chave))

            self._atualizar_graficos(estado_atual)
        finally:
            self.banco.desconectar()

    def _atualizar_graficos(self, estado_atual: dict[str, list[str]]) -> None:
        for widget, qb, formatador in self._graficos:
            sql, params = qb.aplicar_filtros_dashboard(estado_atual).construir()
            resultado = self.banco.executar_select(sql, params)

            if isinstance(widget, CardKPI):
                valor = resultado[0][0] if resultado and resultado[0] else 0
                texto = formatador(valor) if formatador else str(valor if valor is not None else 0)
                widget.set_texto_kpi(texto)
            else:
                if formatador is formatar_coluna_mes:
                    resultado = formatar_coluna_mes(resultado)
                widget.atulizar_dados(resultado)
