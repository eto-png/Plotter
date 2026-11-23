# model/services/utilities.py

MESES_PARA_NUM = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
    "set": "09", "out": "10", "nov": "11", "dez": "12"
}

NUM_PARA_MES = {num: mes for mes, num in MESES_PARA_NUM.items()}


def converter_meses_para_iso(meses_exibicao: list[str]) -> list[str]:
    """
    Ida (Interface -> SQL):
    Converte ['jan/2026', 'mar/2026'] para ['2026-01', '2026-03'].
    """
    datas_iso = []
    for item in meses_exibicao:
        partes = str(item).strip().lower().split("/")
        if len(partes) == 2 and partes[0] in MESES_PARA_NUM:
            datas_iso.append(f"{partes[1]}-{MESES_PARA_NUM[partes[0]]}")
    return datas_iso


def formatar_iso_para_mes(valor_iso: str) -> str:
    """
    Volta (SQL -> Interface):
    Converte '2026-01' para 'jan/2026'.
    """
    if not valor_iso or "-" not in str(valor_iso):
        return str(valor_iso)
    ano, mes_num = str(valor_iso).split("-")[:2]
    return f"{NUM_PARA_MES.get(mes_num, mes_num)}/{ano}"


def formatar_coluna_mes(linhas: list, indice_coluna: int = 0) -> list:
    """
    Recebe o retorno bruto do banco [( '2026-01', 1500.0 ), ...] ou [('2026-01',), ...]
    e converte a coluna de data indicada para o padrão 'jan/2026'.
    """
    resultado = []
    for row in linhas:
        if isinstance(row, (tuple, list)):
            lista_row = list(row)
            lista_row[indice_coluna] = formatar_iso_para_mes(lista_row[indice_coluna])
            resultado.append(tuple(lista_row))
        else:
            resultado.append(formatar_iso_para_mes(row))
    return resultado


def formatar_moeda_brl(valor: float | int | None) -> str:
    """Converte 1250.5 para 'R$ 1.250,50'."""
    numero = float(valor or 0)
    return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")