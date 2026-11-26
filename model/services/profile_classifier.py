import json
import os
import re
import sqlite3
from pathlib import Path

import pandas as pd
from llama_cpp import Llama

from config.paths import AI_DIR, DASHBOARD_MODELS_DIR, SCHEMA_DIR


class BusinessProfileClassifier:
    """
    Classificador de Perfil de Negócio por IA (Qwen 2.5 3B Instruct - ChatML).
    Identifica qual template em `static/dashboard_models/` melhor representa
    a planilha ou banco de vendas ingerido.
    """

    FALLBACK_PERFIL = "alto_giro"

    _PADROES_COLUNA = {
        "produto": r"(?i)\b(produto|nm_produto|item|mercadoria|ve[ií]culo|carro|pe[çc]a|material|descri[çc][aã]o)\b",
        "categoria": r"(?i)\b(categoria|nm_categoria|marca|grupo|tipo|linha|departamento|atributo|cor|tamanho)\b",
        "vendedor": r"(?i)\b(vendedor|nm_vendedor|atendente|consultor|respons[aá]vel)\b",
        "localidade": r"(?i)\b(localidade|nm_localidade|cidade|estado|uf|filial|loja|regi[aã]o|bairro)\b",
        "vl_custo": r"(?i)\b((valor|val|vlr|vl|vr|pre[çc]o)[\s_\-\.]*)?(custo|cst)\b",
        "vl_desconto": r"(?i)\b(desconto|vl_desconto|valor_desconto|pc_desconto)\b",
        "vl_total": r"(?i)\b((valor|val|vlr|vl|vr|pre[çc]o)[\s_\-\.]*(de[\s_\-\.]+)?(total|venda|final|l[ií]quido)|total|vl_total)\b",
        "vl_unitario": r"(?i)\b((valor|val|vlr|vl|vr|pre[çc]o)[\s_\-\.]*(unit[aá]rio|unit|unt|un)|vl_preco|pre[çc]o)\b",
        "qt_produto": r"(?i)\b(quantidade|qt_produto|qtd|qtde)\b",
    }

    def __init__(self, model_filename: str = "qwen2.5-3b-instruct-q4_k_m.gguf"):
        self.model_path = AI_DIR / model_filename
        self._llm: Llama | None = None
        self.perfis_disponiveis = self._carregar_perfis_disponiveis()

    @staticmethod
    def _carregar_perfis_disponiveis() -> dict[str, str]:
        """Lê todos os *.json em DASHBOARD_MODELS_DIR e monta {id: descricao_ia}."""
        perfis: dict[str, str] = {}
        if not DASHBOARD_MODELS_DIR.exists():
            return perfis

        for caminho in sorted(DASHBOARD_MODELS_DIR.glob("*.json")):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                perfil_id = dados.get("id")
                descricao_ia = dados.get("descricao_ia")
                if isinstance(perfil_id, str) and isinstance(descricao_ia, str):
                    perfis[perfil_id] = descricao_ia
            except (OSError, json.JSONDecodeError) as exc:
                print(f"[BusinessProfileClassifier] Erro ao ler {caminho.name}: {exc}")

        return perfis

    def _get_llm(self) -> Llama | None:
        if not self.model_path.exists():
            print(
                f"[BusinessProfileClassifier] Modelo de IA não encontrado em: {self.model_path}. "
                f"Usando fallback '{self.FALLBACK_PERFIL}'."
            )
            return None

        if self._llm is None:
            num_threads = max(1, os.cpu_count() or 4)
            self._llm = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,
                n_threads=num_threads,
                verbose=False,
            )
        return self._llm

    @classmethod
    def _encontrar_coluna(
        cls,
        df: pd.DataFrame,
        chave: str,
        mapa: dict | None = None,
        excluir: set[str] | None = None,
    ) -> str | None:
        excluir = excluir or set()
        if mapa:
            for col_planilha, entidade in mapa.items():
                if entidade == chave and col_planilha in df.columns and col_planilha not in excluir:
                    return col_planilha

        padrao = cls._PADROES_COLUNA.get(chave)
        if not padrao:
            return None

        for col in df.columns:
            if col not in excluir and re.search(padrao, str(col)):
                return col
        return None

    @staticmethod
    def _serie_numerica(serie: pd.Series) -> pd.Series:
        if pd.api.types.is_numeric_dtype(serie):
            return pd.to_numeric(serie, errors="coerce")

        limpa = (
            serie.astype(str)
            .str.replace(r"[R$\s]", "", regex=True)
            .str.replace(r"\.(?=\d{3}(?:,|$))", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        return pd.to_numeric(limpa, errors="coerce")

    def extrair_contexto_negocio(
        self,
        df: pd.DataFrame,
        mapa: dict | None = None,
    ) -> dict:
        """Extrai indicadores leves e amostras de um DataFrame normalizado."""
        total_transacoes = int(len(df))

        col_produto = self._encontrar_coluna(df, "produto", mapa)
        usadas = {col_produto} if col_produto else set()
        col_categoria = self._encontrar_coluna(df, "categoria", mapa, excluir=usadas)
        col_vendedor = self._encontrar_coluna(df, "vendedor", mapa, excluir=usadas)
        col_localidade = self._encontrar_coluna(df, "localidade", mapa, excluir=usadas)
        col_custo = self._encontrar_coluna(df, "vl_custo", mapa, excluir=usadas)
        col_desconto = self._encontrar_coluna(df, "vl_desconto", mapa, excluir=usadas)

        if col_produto and not df[col_produto].dropna().empty:
            serie_produtos = df[col_produto].dropna().astype(str).str.strip()
            serie_produtos = serie_produtos[serie_produtos != ""]
            produtos_unicos = int(serie_produtos.nunique())
            amostra_produtos = serie_produtos.unique()[:5].tolist()
        else:
            produtos_unicos = 0
            amostra_produtos = []

        taxa_repeticao_produto = round(total_transacoes / max(produtos_unicos, 1), 2)

        if col_categoria and not df[col_categoria].dropna().empty:
            serie_cat = df[col_categoria].dropna().astype(str).str.strip()
            serie_cat = serie_cat[serie_cat != ""]
            amostra_categorias = serie_cat.unique()[:5].tolist()
        else:
            amostra_categorias = []

        ticket_medio_estimado = 0.0
        col_total = self._encontrar_coluna(df, "vl_total", mapa)
        col_unitario = self._encontrar_coluna(df, "vl_unitario", mapa)
        col_qtd = self._encontrar_coluna(df, "qt_produto", mapa)

        if col_total and not df[col_total].dropna().empty:
            valores = self._serie_numerica(df[col_total]).dropna()
            if not valores.empty:
                ticket_medio_estimado = round(float(valores.mean()), 2)
        elif col_unitario and not df[col_unitario].dropna().empty:
            unitarios = self._serie_numerica(df[col_unitario])
            if col_qtd and not df[col_qtd].dropna().empty:
                qtds = self._serie_numerica(df[col_qtd]).fillna(1.0)
                valores = (unitarios * qtds).dropna()
            else:
                valores = unitarios.dropna()
            if not valores.empty:
                ticket_medio_estimado = round(float(valores.mean()), 2)

        colunas_presentes = []
        checagens = [
            ("produto", col_produto),
            ("categoria", col_categoria),
            ("vendedor", col_vendedor),
            ("localidade", col_localidade),
            ("vl_custo", col_custo),
            ("vl_desconto", col_desconto),
        ]
        for nome_entidade, col_nome in checagens:
            if col_nome and not df[col_nome].dropna().empty:
                colunas_presentes.append(nome_entidade)

        return {
            "total_transacoes": total_transacoes,
            "produtos_unicos": produtos_unicos,
            "taxa_repeticao_produto": taxa_repeticao_produto,
            "ticket_medio_estimado": ticket_medio_estimado,
            "colunas_presentes": colunas_presentes,
            "amostra_produtos": amostra_produtos,
            "amostra_categorias": amostra_categorias,
        }

    def extrair_contexto_do_banco(self, db_path: str | Path) -> dict:
        """Extrai o mesmo contexto compacto diretamente de um banco SQLite .db."""
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            total_transacoes = int(cur.execute("SELECT COUNT(*) FROM venda").fetchone()[0])
            produtos_unicos = int(cur.execute("SELECT COUNT(DISTINCT nm_produto) FROM produto").fetchone()[0])
            taxa_repeticao_produto = round(total_transacoes / max(produtos_unicos, 1), 2)

            ticket_row = cur.execute(
                "SELECT COALESCE(AVG(vl_total), 0) FROM venda WHERE vl_total IS NOT NULL"
            ).fetchone()
            ticket_medio_estimado = round(float(ticket_row[0] or 0.0), 2)

            amostra_produtos = [
                row[0]
                for row in cur.execute(
                    "SELECT DISTINCT nm_produto FROM produto WHERE nm_produto IS NOT NULL LIMIT 5"
                ).fetchall()
            ]
            amostra_categorias = [
                row[0]
                for row in cur.execute(
                    "SELECT DISTINCT nm_categoria FROM categoria WHERE nm_categoria IS NOT NULL LIMIT 5"
                ).fetchall()
            ]

            colunas_presentes = []
            if produtos_unicos > 0:
                colunas_presentes.append("produto")
            if amostra_categorias:
                colunas_presentes.append("categoria")
            if cur.execute("SELECT COUNT(*) FROM vendedor").fetchone()[0] > 0:
                colunas_presentes.append("vendedor")
            if cur.execute("SELECT COUNT(*) FROM localidade").fetchone()[0] > 0:
                colunas_presentes.append("localidade")
            if cur.execute("SELECT COUNT(*) FROM produto WHERE vl_custo IS NOT NULL").fetchone()[0] > 0:
                colunas_presentes.append("vl_custo")
            if cur.execute("SELECT COUNT(*) FROM venda WHERE vl_desconto IS NOT NULL").fetchone()[0] > 0:
                colunas_presentes.append("vl_desconto")

            return {
                "total_transacoes": total_transacoes,
                "produtos_unicos": produtos_unicos,
                "taxa_repeticao_produto": taxa_repeticao_produto,
                "ticket_medio_estimado": ticket_medio_estimado,
                "colunas_presentes": colunas_presentes,
                "amostra_produtos": amostra_produtos,
                "amostra_categorias": amostra_categorias,
            }
        finally:
            conn.close()

    def classificar(self, contexto: dict) -> str:
        """Classifica o contexto do negócio usando o prompt fixo ChatML."""
        if not self.perfis_disponiveis:
            return self.FALLBACK_PERFIL

        llm = self._get_llm()
        if llm is None:
            return self.FALLBACK_PERFIL

        prompt = f"""<|im_start|>system
Você é um Especialista em Business Intelligence classificando o perfil comercial de uma planilha de vendas para escolher o melhor template de dashboard.

PERFIS DE DASHBOARD DISPONÍVEIS:
{json.dumps(self.perfis_disponiveis, ensure_ascii=False, indent=2)}

EXEMPLOS DE CLASSIFICAÇÃO:

Amostra ["Honda Civic 2020", "Fiat Argo 2022"], taxa_repeticao_produto: 1.05, ticket_medio: 65000.0 -> {{"perfil": "bens_unicos"}}

Amostra ["Arroz 5kg", "Coca-Cola 2L"], taxa_repeticao_produto: 18.4, ticket_medio: 42.5 -> {{"perfil": "alto_giro"}}

Amostra ["Camiseta Polo", "Calça Jeans"], categorias ["M", "Preto", "Zara"], tem custo -> {{"perfil": "grade_variantes"}}

Amostra ["Cimento CP-II 50kg", "Tijolo Baiano"], tem localidade e descontos -> {{"perfil": "atacado_pedidos"}}

REGRAS OBRIGATÓRIAS:

Analise os indicadores e amostras enviados pelo usuário e escolha EXATAMENTE UM dos IDs em PERFIS DE DASHBOARD DISPONÍVEIS.

Retorne EXCLUSIVAMENTE um objeto JSON válido no formato: {{"perfil": "<id_escolhido>"}}

Nunca invente IDs fora da lista oficial. Sem textos explicativos.
<|im_end|>
<|im_start|>user
Dados resumidos do negócio:
{json.dumps(contexto, ensure_ascii=False, indent=2)}
<|im_end|>
<|im_start|>assistant
{{"""

        try:
            output = llm(
                prompt,
                max_tokens=128,
                temperature=0.0,
                stop=["<|im_end|>", "```"],
            )
            raw_text = "{" + output["choices"][0]["text"].strip()
            if raw_text.startswith("{{"):
                raw_text = raw_text[1:]

            if not raw_text.endswith("}"):
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                raw_text = match.group(0) if match else raw_text + "\n}"

            dados = json.loads(raw_text)
            perfil = dados.get("perfil")
            if isinstance(perfil, str) and perfil in self.perfis_disponiveis:
                return perfil

            print(
                f"[BusinessProfileClassifier] Perfil inválido '{perfil}'. "
                f"Usando fallback '{self.FALLBACK_PERFIL}'."
            )
            return self.FALLBACK_PERFIL
        except (json.JSONDecodeError, Exception) as exc:
            print(
                f"[BusinessProfileClassifier] Falha na classificação ({exc}). "
                f"Usando fallback '{self.FALLBACK_PERFIL}'."
            )
            return self.FALLBACK_PERFIL

    def classificar_planilha(
        self,
        df: pd.DataFrame,
        mapa: dict | None = None,
    ) -> str:
        """Extrai contexto do DataFrame e retorna o ID do perfil classificado."""
        contexto = self.extrair_contexto_negocio(df, mapa=mapa)
        return self.classificar(contexto)

    @staticmethod
    def salvar_perfil_schema(
        nome_dashboard: str,
        perfil: str,
        mapa: dict | None = None,
    ) -> Path:
        """Persiste 'perfil_dashboard' em data/schema/<nome_dashboard>_schema.json."""
        SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
        schema_path = SCHEMA_DIR / f"{nome_dashboard}_schema.json"

        schema_data: dict = {}
        if schema_path.exists():
            try:
                conteudo = schema_path.read_text(encoding="utf-8").strip()
                if conteudo:
                    schema_data = json.loads(conteudo)
            except (OSError, json.JSONDecodeError):
                schema_data = {}

        if mapa is not None and "mapeamento" not in schema_data:
            schema_data["mapeamento"] = mapa

        schema_data["perfil_dashboard"] = perfil

        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)

        return schema_path
