from model.services.utilities import converter_meses_para_iso

class QueryBuilder:
    """
    Serviço responsável por montar consultas SQL dinâmicas e seus parâmetros
    de forma segura, sem depender diretamente da camada de conexão com o banco.
    """

    MESES_PARA_NUM = {
        "jan": "01", "fev": "02", "mar": "03", "abr": "04",
        "mai": "05", "jun": "06", "jul": "07", "ago": "08",
        "set": "09", "out": "10", "nov": "11", "dez": "12"
    }

    def __init__(self, query_base: str, group_by: str = "", order_by: str = ""):
        self.query_base = query_base.strip()
        self.group_by = group_by.strip()
        self.order_by = order_by.strip()
        self._condicoes: list[str] = []
        self._parametros: list = []

    @classmethod
    def converter_meses_para_iso(cls, meses_exibicao: list[str]) -> list[str]:
        """Converte ['jan/2026', 'mar/2026'] para ['2026-01', '2026-03']."""
        datas_iso = []
        for item in meses_exibicao:
            partes = item.strip().lower().split("/")
            if len(partes) == 2 and partes[0] in cls.MESES_PARA_NUM:
                mes_num = cls.MESES_PARA_NUM[partes[0]]
                ano = partes[1]
                datas_iso.append(f"{ano}-{mes_num}")
        return datas_iso

    def limpar_filtros(self) -> "QueryBuilder":
        """Reseta todas as condições WHERE e parâmetros acumulados."""
        self._condicoes.clear()
        self._parametros.clear()
        return self

    def adicionar_filtro_in(
        self,
        expressao_coluna: str,
        valores: list,
        ignorar_vazio: bool = False
    ) -> "QueryBuilder":
        if not valores:
            if not ignorar_vazio:
                self._condicoes.append("1 = 0")
            return self

        placeholders = ", ".join(["?"] * len(valores))
        self._condicoes.append(f"{expressao_coluna} IN ({placeholders})")
        self._parametros.extend(valores)
        return self

    def adicionar_filtro_categoria(
        self,
        categorias: list[str],
        ignorar_vazio: bool = False
    ) -> "QueryBuilder":
        if not categorias:
            if not ignorar_vazio:
                self._condicoes.append("1 = 0")
            return self

        placeholders = ", ".join(["?"] * len(categorias))
        condicao_exists = f"""EXISTS (
            SELECT 1
            FROM lista_categoria lc
            JOIN categoria c ON lc.cd_categoria = c.cd_categoria
            WHERE lc.cd_produto = p.cd_produto
              AND c.nm_categoria IN ({placeholders})
        )"""
        self._condicoes.append(condicao_exists)
        self._parametros.extend(categorias)
        return self

    def adicionar_filtro_customizado(self, condicao_sql: str, params: list = None) -> "QueryBuilder":
        """Adiciona uma condição SQL arbitrária e seus respectivos parâmetros."""
        if condicao_sql and condicao_sql.strip():
            self._condicoes.append(condicao_sql.strip())
            if params:
                self._parametros.extend(params)
        return self

    def aplicar_filtros_dashboard(
        self,
        estado_filtros: dict[str, list | None],
        ignorar: str = "",
        modo_opcoes: bool = False
    ) -> "QueryBuilder":
        """
        - modo_opcoes=False (padrão, para gráficos): lista vazia [] injeta '1 = 0' e zera o gráfico.
        - modo_opcoes=True (para dropdowns): lista vazia [] é ignorada para não apagar as opções dos outros filtros.
        """
        self.limpar_filtros()

        if ignorar != "mes" and estado_filtros.get("mes") is not None:
            datas_iso = converter_meses_para_iso(estado_filtros["mes"])
            self.adicionar_filtro_in(
                "strftime('%Y-%m', v.dt_venda)",
                datas_iso,
                ignorar_vazio=modo_opcoes
            )

        if ignorar != "produto" and estado_filtros.get("produto") is not None:
            self.adicionar_filtro_in(
                "p.nm_produto",
                estado_filtros["produto"],
                ignorar_vazio=modo_opcoes
            )

        if ignorar != "categoria" and estado_filtros.get("categoria") is not None:
            self.adicionar_filtro_categoria(
                estado_filtros["categoria"],
                ignorar_vazio=modo_opcoes
            )

        if ignorar != "vendedor" and estado_filtros.get("vendedor") is not None:
            self.adicionar_filtro_in(
                "vend.nm_vendedor",
                estado_filtros["vendedor"],
                ignorar_vazio=modo_opcoes
            )

        if ignorar != "localidade" and estado_filtros.get("localidade") is not None:
            self.adicionar_filtro_in(
                "loc.nm_localidade",
                estado_filtros["localidade"],
                ignorar_vazio=modo_opcoes
            )

        return self

    def construir(self) -> tuple[str, list]:
        """Retorna (query_sql_final, lista_de_parametros) pronta para o cursor.execute()."""
        partes = [self.query_base]

        if self._condicoes:
            conector = "AND " if "WHERE" in self.query_base.upper() else "WHERE "
            partes.append(conector + "\n  AND ".join(self._condicoes))

        if self.group_by:
            partes.append(f"GROUP BY {self.group_by}")

        if self.order_by:
            partes.append(f"ORDER BY {self.order_by}")

        return "\n".join(partes), list(self._parametros)