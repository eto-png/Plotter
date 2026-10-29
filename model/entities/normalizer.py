# model/services/normalizer.py

import json
import os
import re
import pandas as pd
from pathlib import Path
from llama_cpp import Llama
from config.paths import ROOT_DIR


class SemanticNormalizer:
    """
    Normalizador Semântico Otimizado para Qwen 2.5 (Formato ChatML).
    Executa exclusivamente em memória RAM.
    """

    def __init__(self, model_filename: str = "qwen2.5-3b-instruct-q4_k_m.gguf"):
        self.model_path = ROOT_DIR / "ai" / model_filename
        self._llm = None
        self.mappings = {}

    def _get_llm(self) -> Llama:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo de IA não encontrado em: {self.model_path}. "
                "Execute 'python setup_ia.py' primeiro para baixar o modelo."
            )

        if self._llm is None:
            num_threads = max(1, os.cpu_count() or 4)
            self._llm = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,
                n_threads=num_threads,
                verbose=False
            )
        return self._llm

    def normalize_column(self, df: pd.DataFrame, col_name: str) -> pd.DataFrame:
        if col_name not in df.columns:
            return df

        clean_df = df.copy()
        raw_values = clean_df[col_name].dropna().astype(str).str.strip().unique().tolist()

        if not raw_values:
            return clean_df

        mapping = self._process_with_ai(raw_values, col_name)
        self.mappings[col_name] = mapping

        clean_df[col_name] = clean_df[col_name].replace(mapping)
        return clean_df

    def _process_with_ai(self, values: list, col_name: str) -> dict:
        llm = self._get_llm()

        # Prompt formatado estritamente com os marcadores ChatML do Qwen 2.5
        prompt = f"""<|im_start|>system
Você é um assistente especialista em sanitização e padronização de dados de vendas em português.
Sua tarefa é analisar uma lista de termos e agrupar erros de digitação, siglas, abreviações, nomes incompletos e diferenças de maiúsculas/minúsculas sob um ÚNICO nome oficial padronizado (em Title Case).

Exemplo de Entrada:
Coluna: 'forma_de_pagamento'
Termos: ["CC", "cartao de credito", "Pix", "pix", "CD", "cartao debito"]

Exemplo de Saída JSON:
{{
  "CC": "Cartão de Crédito",
  "cartao de credito": "Cartão de Crédito",
  "Pix": "Pix",
  "pix": "Pix",
  "CD": "Cartão de Débito",
  "cartao debito": "Cartão de Débito"
}}
<|im_end|>
<|im_start|>user
Coluna: '{col_name}'
Termos para padronizar: {values}

Retorne EXCLUSIVAMENTE o objeto JSON contendo o mapeamento de TODOS os termos originais da lista para seus respectivos nomes padronizados. Não escreva nenhuma explicação antes ou depois do JSON.
<|im_end|>
<|im_start|>assistant
{{"""

        output = llm(
            prompt,
            max_tokens=1536,
            temperature=0.0,
            stop=["<|im_end|>", "```"]
        )

        raw_text = "{" + output["choices"][0]["text"].strip()

        if not raw_text.endswith("}"):
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)
            else:
                raw_text += "\n}"

        try:
            mapping = json.loads(raw_text)
            return {str(k): str(v) for k, v in mapping.items()}
        except json.JSONDecodeError:
            print(f"[AVISO] Falha no parse do JSON para a coluna '{col_name}'. Mantendo originais.")
            return {v: v for v in values}