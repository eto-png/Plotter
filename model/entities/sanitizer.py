import re
import pandas as pd
from pathlib import Path


class GenericDataSanitizer:
    """
    Higieniza e extrai dados de qualquer planilha por inferência dinâmica de tipos,
    independente do setor ou colunas da empresa.
    """

    @staticmethod
    def extract_from_file(file_path: Path) -> pd.DataFrame:
        """
        Extrai os dados de uma planilha (CSV ou Excel) e os carrega em um DataFrame.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        ext = path.suffix.lower()
        if ext == ".csv":
            try:
                return pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding="latin-1")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}. Use .csv ou .xlsx")

    @staticmethod
    def sanitize(df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa o pipeline completo de limpeza no DataFrame.
        """
        clean_df = df.copy()

        # 1. Normalização e desduplicação de cabeçalhos
        raw_cleaned_cols = [
            GenericDataSanitizer._clean_column_name(col) for col in clean_df.columns
        ]
        clean_df.columns = GenericDataSanitizer._make_columns_unique(raw_cleaned_cols)

        # 2. Sanitização de conteúdo coluna por coluna
        for col in clean_df.columns:
            clean_df[col] = GenericDataSanitizer._sanitize_series(clean_df[col])

        return clean_df

    @staticmethod
    def _make_columns_unique(columns: list) -> list:
        """
        Garante que não existam colunas com nomes duplicados no DataFrame.
        Exemplo: ['comissao', 'comissao'] -> ['comissao', 'comissao_2']
        """
        seen = {}
        unique_cols = []
        for col in columns:
            if col in seen:
                seen[col] += 1
                unique_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 1
                unique_cols.append(col)
        return unique_cols

    @staticmethod
    def _clean_column_name(col_name: str) -> str:
        """
        Converte cabeçalhos para snake_case limpo.
        Exemplo: 'Preço Venda (R$)' -> 'preco_venda'
        """
        col = str(col_name).strip().lower()

        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u',
            'ç': 'c'
        }
        for char, repl in replacements.items():
            col = col.replace(char, repl)

        # Remove qualificadores/unidades entre parênteses: (R$), (%), (kg)
        col = re.sub(r'\s*\([^)]*\)', '', col)

        # Substitui caracteres não alfanuméricos por underline
        col = re.sub(r'[^a-z0-9]', '_', col)

        # Remove underlines duplicados e das pontas
        return re.sub(r'_+', '_', col).strip('_')

    @staticmethod
    def _sanitize_series(s: pd.Series) -> pd.Series:
        """
        Inspeciona a amostra dos dados de uma coluna e aplica a conversão adequada.
        """
        if s.dropna().empty:
            return s

        sample = s.dropna().astype(str)

        # A. Detecção de Moedas ou Percentuais (ex: 'R$ 1.200,50' ou '2,5%')
        is_currency_or_percent = sample.str.contains(r'R\$\s*[\d\.,]+|%').mean() > 0.3
        if is_currency_or_percent:
            cleaned_str = (
                s.astype(str)
                .str.replace(r'R\$\s*', '', regex=True)
                .str.replace(r'%', '', regex=False)
                .str.replace(r'\.', '', regex=True)  # Remove ponto de milhar PT-BR
                .str.replace(',', '.', regex=False)  # Troca vírgula decimal por ponto
                .str.strip()
            )
            return pd.to_numeric(cleaned_str, errors='ignore')

        # B. Detecção de Números Flutuantes em PT-BR sem prefixo R$ (ex: '120,50')
        is_br_float = sample.str.match(r'^-?\d+(\.\d+)*,\d+$').mean() > 0.5
        if is_br_float:
            cleaned_str = (
                s.astype(str)
                .str.replace(r'\.', '', regex=True)
                .str.replace(',', '.', regex=False)
                .str.strip()
            )
            return pd.to_numeric(cleaned_str, errors='ignore')

        # C. Detecção de Datas (Ex: '2023-10-01' ou '01/10/2023')
        is_date = sample.str.match(r'^\d{4}-\d{2}-\d{2}|^\d{2}/\d{2}/\d{4}').mean() > 0.5
        if is_date:
            return pd.to_datetime(s, errors='ignore')

        # D. Detecção de Booleanos (Sim/Não, S/N, True/False)
        upper_sample = sample.str.upper().str.strip()
        if set(upper_sample.unique()).issubset({'SIM', 'NAO', 'NÃO', 'S', 'N', 'TRUE', 'FALSE'}):
            return upper_sample.isin(['SIM', 'S', 'TRUE'])

        return s