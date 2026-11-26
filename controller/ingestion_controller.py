import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

from config.paths import SCHEMA_DIR
from model.entities.mapper import SchemaMapper
from model.entities.normalizer import SemanticNormalizer
from model.entities.repository import GenericDatabaseRepository
from model.services.profile_classifier import BusinessProfileClassifier
from model.services.sanitizer import GenericDataSanitizer


class IngestionController:
    """
    Orquestrador ponta a ponta da ingestão de planilhas:
    leitura -> sanitização -> normalização semântica -> mapeamento de entidades ->
    persistência no SQLite -> classificação de perfil -> criação do _schema.json.
    """

    def __init__(
        self,
        normalizer: SemanticNormalizer | None = None,
        mapper: SchemaMapper | None = None,
        classifier: BusinessProfileClassifier | None = None,
    ):
        self.normalizer = normalizer or SemanticNormalizer()
        self.mapper = mapper or SchemaMapper()
        self.classifier = classifier or BusinessProfileClassifier()

    @staticmethod
    def gerar_id_dashboard(file_path: str | Path) -> str:
        """Gera um identificador seguro e único a partir do nome da planilha + timestamp."""
        stem = Path(file_path).stem
        sem_acento = (
            unicodedata.normalize("NFKD", stem)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acento).strip("_").lower()
        slug = slug or "dashboard"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}"

    @staticmethod
    def gerar_nome_exibicao(file_path: str | Path) -> str:
        """Gera um nome legível para exibição na interface a partir do nome do arquivo."""
        stem = Path(file_path).stem
        limpo = re.sub(r"[_\-]+", " ", stem)
        limpo = re.sub(r"\s+", " ", limpo).strip()
        return limpo or "Dashboard"

    @staticmethod
    def _notificar(
        on_progress: Callable[[int, int, str], None] | None,
        step: int,
        percentage: int,
        message: str,
    ) -> None:
        if on_progress is not None:
            on_progress(step, percentage, message)

    def executar(
        self,
        file_path: str | Path,
        dashboard_id: str | None = None,
        nome_exibicao: str | None = None,
        normalizar: bool = True,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> dict:
        """
        Executa o pipeline completo de ingestão e gera `data/schema/<id>_schema.json`.
        Retorna um dicionário com `id`, `schema_path` e `schema`.
        """
        caminho = Path(file_path)
        dash_id = dashboard_id or self.gerar_id_dashboard(caminho)
        titulo_exibicao = nome_exibicao or self.gerar_nome_exibicao(caminho)
        arquivo_original = caminho.name

        # Etapa 0: Leitura e sanitização
        df_bruto = GenericDataSanitizer.extract_from_file(caminho)
        df_sanitizado = GenericDataSanitizer.sanitize(df_bruto)
        self._notificar(on_progress, 0, 33, "Arquivo lido")

        # Etapa 1: Normalização semântica, mapeamento e classificação
        df_final = df_sanitizado.copy()
        normalizacoes: dict = {}
        if normalizar:
            colunas_texto = [
                col
                for col in df_final.columns
                if pd.api.types.is_object_dtype(df_final[col])
                or pd.api.types.is_string_dtype(df_final[col])
            ]
            for col in colunas_texto:
                df_final = self.normalizer.normalize_column(df_final, col_name=col)
            normalizacoes = dict(self.normalizer.mappings)

        mapeamento = self.mapper.mapear_entidades(df_final)
        perfil, origem_classificacao = self.classifier.classificar_planilha_com_origem(
            df_final, mapa=mapeamento
        )
        self._notificar(on_progress, 1, 66, "Interpretação dos dados")

        # Etapa 2: Persistência no banco e criação do _schema.json
        repository = GenericDatabaseRepository(dash_id)
        repository.inserir_extremidades(df_final, mapeamento)
        repository.inserir_vendas(df_final, mapeamento, salvar_schema=False)

        schema_path = self.classifier.salvar_perfil_schema(
            nome_dashboard=dash_id,
            perfil=perfil,
            mapa=mapeamento,
            nome_exibicao=titulo_exibicao,
            arquivo_original=arquivo_original,
            origem_classificacao=origem_classificacao,
            normalizacoes=normalizacoes,
        )
        self._notificar(on_progress, 2, 100, "Criação dos gráficos")

        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
        return {
            "id": dash_id,
            "schema_path": str(schema_path),
            "schema": schema_data,
        }

    @staticmethod
    def carregar_schema(dashboard_id: str) -> dict | None:
        """Lê o arquivo `<id>_schema.json` em `data/schema/`."""
        schema_path = SCHEMA_DIR / f"{dashboard_id}_schema.json"
        if not schema_path.exists():
            return None
        try:
            conteudo = schema_path.read_text(encoding="utf-8").strip()
            return json.loads(conteudo) if conteudo else None
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def listar_dashboards() -> list[dict]:
        """Lista todos os schemas válidos em `data/schema/`, ordenados do mais recente ao mais antigo."""
        if not SCHEMA_DIR.exists():
            return []

        dashboards: list[dict] = []
        for caminho in SCHEMA_DIR.glob("*_schema.json"):
            try:
                conteudo = caminho.read_text(encoding="utf-8").strip()
                if not conteudo:
                    continue
                dados = json.loads(conteudo)
                if isinstance(dados, dict) and dados.get("id"):
                    dashboards.append(dados)
            except (OSError, json.JSONDecodeError):
                continue

        dashboards.sort(
            key=lambda d: (d.get("metadados") or {}).get("criado_em", ""),
            reverse=True,
        )
        return dashboards

    @staticmethod
    def atualizar_metadados(
        dashboard_id: str,
        nome_exibicao: str | None = None,
        perfil_dashboard: str | None = None,
        origem_classificacao: str | None = None,
    ) -> dict | None:
        """Atualiza campos editáveis de `<id>_schema.json` preservando o restante."""
        schema_path = SCHEMA_DIR / f"{dashboard_id}_schema.json"
        dados = IngestionController.carregar_schema(dashboard_id)
        if dados is None:
            return None

        metadados = dados.setdefault("metadados", {})
        if nome_exibicao is not None:
            metadados["nome_exibicao"] = nome_exibicao
        if perfil_dashboard is not None:
            dados["perfil_dashboard"] = perfil_dashboard
        if origem_classificacao is not None:
            metadados["origem_classificacao"] = origem_classificacao

        metadados["atualizado_em"] = datetime.now().astimezone().isoformat(timespec="seconds")

        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return dados
