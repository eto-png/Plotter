# model/services/schema_mapper.py

import json
import re
import pandas as pd
from pathlib import Path
from llama_cpp import Llama
from config.paths import ROOT_DIR

class SchemaMapper:
    """
    Tradutor de Entidades Únicas: Lê as colunas da planilha e identifica APENAS 
    se a coluna representa uma das tabelas de dimensão (extremidades) do modelo.
    """
    
    # Foco estrito nas tabelas de dimensão (entidades únicas)
    TABELAS_DIMENSAO = {
        "produto": "Representa o item, veículo, mercadoria ou serviço vendido.",
        "categoria": "Representa o grupo, classificação, tipo, fabricante ou marca do produto.",
        "vendedor": "Representa o funcionário, atendente ou responsável pela venda.",
        "localidade": "Representa a loja, filial, cidade ou ponto de venda.",
        "forma_pagamento": "Representa a forma de pagamento utilizada na transação."
    }

    def __init__(self, model_filename: str = "qwen2.5-3b-instruct-q4_k_m.gguf"):
        self.model_path = ROOT_DIR / "ai" / model_filename
        self._llm = None
        self.valid_targets = list(self.TABELAS_DIMENSAO.keys())

    def _get_llm(self) -> Llama:
        if self._llm is None and self.model_path.exists():
            self._llm = Llama(model_path=str(self.model_path), n_ctx=2048, verbose=False)
        return self._llm

    def extrair_amostras(self, df: pd.DataFrame) -> dict:
        """Extrai os cabeçalhos e até 2 valores de exemplo para contexto."""
        return {
            col: df[col].dropna().astype(str).unique()[:2].tolist() 
            for col in df.columns if not df[col].dropna().empty
        }

    def mapear_entidades(self, df: pd.DataFrame) -> dict:
        llm = self._get_llm()
        if not llm: 
            return {}

        amostras_planilha = self.extrair_amostras(df)
        
        prompt = f"""<|im_start|>system
Você é um Arquiteto de Dados mapeando colunas de uma planilha para tabelas de um banco de dados.

TABELAS DE ENTIDADES ÚNICAS DISPONÍVEIS:
{json.dumps(self.TABELAS_DIMENSAO, ensure_ascii=False, indent=2)}

REGRAS:
1. Avalie se a coluna representa o NOME IDENTIFICADOR de uma das entidades acima. Exemplo: "carro" ou "peça" -> "produto"; "marca" -> "categoria"; "atendente" -> "vendedor". Pode ser que mais de uma coluna represente a mesma entidade, mas cada coluna deve ser mapeada individualmente.
2. Atributos da transação (fatos) como: data, quantidade, valor da venda, custo, descontos ou observações DEVEM ser mapeados como null.
3. Retorne EXCLUSIVAMENTE um objeto JSON onde a CHAVE é o nome da coluna da planilha e o VALOR é o nome da tabela exata ou null.
<|im_end|>
<|im_start|>user
COLUNAS DA PLANILHA (Nome -> Amostras):
{json.dumps(amostras_planilha, ensure_ascii=False, indent=2)}
<|im_end|>
<|im_start|>assistant
{{"""

        output = llm(prompt, max_tokens=1024, temperature=0.0, stop=["<|im_end|>", "```"])
        raw_text = "{" + output['choices'][0]['text'].strip()
        
        if not raw_text.endswith("}"):
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            raw_text = match.group(0) if match else raw_text + "\n}"

        try:
            mapeamento_bruto = json.loads(raw_text)
            
            # Filtro anti-alucinação: só aceita as 4 tabelas exatas ou null
            mapeamento_limpo = {}
            for col_planilha, destino in mapeamento_bruto.items():
                if destino in self.valid_targets:
                    mapeamento_limpo[col_planilha] = destino
                else:
                    mapeamento_limpo[col_planilha] = None
                    
            return mapeamento_limpo
        except json.JSONDecodeError:
            print("[SchemaMapper] Erro ao decodificar JSON.")
            return {}