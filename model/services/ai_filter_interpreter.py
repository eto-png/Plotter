"""
Serviço de interpretação de filtros via IA local (Qwen 2.5 3B Instruct).

Recebe um texto em linguagem natural do usuário (ex: "mostra só o mês de outubro")
e, combinado com as opções disponíveis nos filtros do dashboard ativo, retorna
um dicionário indicando quais valores devem ser selecionados em cada filtro.

Formato de retorno:
  {
    "mes": ["out/2024"],          # None significa "todos"
    "categoria": None,
    "produto": None,
    "vendedor": None,
    "localidade": None,
  }

Se a chave não aparecer no retorno da IA, o filtro correspondente não é alterado.
"""

from datetime import datetime
import json
import os
import re
import unicodedata
from pathlib import Path

from config.paths import AI_DIR


# Nomes de mês em português -> prefixo de 3 letras usado no formato "mmm/AAAA"
_MESES_PT = {
    "janeiro": "jan", "fevereiro": "fev", "março": "mar", "marco": "mar",
    "abril": "abr", "maio": "mai", "junho": "jun",
    "julho": "jul", "agosto": "ago", "setembro": "set",
    "outubro": "out", "novembro": "nov", "dezembro": "dez",
}

_ABREV_POR_NUM_MES = {
    1: "jan", 2: "fev", 3: "mar", 4: "abr",
    5: "mai", 6: "jun", 7: "jul", 8: "ago",
    9: "set", 10: "out", 11: "nov", 12: "dez",
}

_NUM_MES_POR_ABREV = {abrev: num for num, abrev in _ABREV_POR_NUM_MES.items()}


def _mes_ano_formatado(ano: int, mes: int) -> str:
    return f"{_ABREV_POR_NUM_MES[mes]}/{ano}"


def _parse_opcao_mes(opcao: str) -> tuple[int, int] | None:
    """Converte 'mmm/AAAA' (ex: 'out/2026') para (ano, mes) ordenável."""
    partes = _normalizar_mes(opcao).split("/")
    if len(partes) != 2:
        return None
    abrev, ano_str = partes
    num_mes = _NUM_MES_POR_ABREV.get(abrev)
    if num_mes is None or not ano_str.isdigit():
        return None
    return (int(ano_str), num_mes)


def _subtrair_meses(ano: int, mes: int, quantidade: int) -> tuple[int, int]:
    """Retorna (ano, mes) após retroceder `quantidade` meses."""
    total_meses = ano * 12 + (mes - 1) - quantidade
    novo_ano, novo_mes_zero = divmod(total_meses, 12)
    return (novo_ano, novo_mes_zero + 1)


def _resolver_meses_relativos(
    texto_usuario: str,
    opcoes_mes: list[str],
    referencia: datetime | None = None,
) -> list[str] | None:
    """
    Resolve expressões temporais relativas de forma determinística contra `opcoes_mes`.

    Retorna:
    - list[str]: opções correspondentes quando uma expressão relativa é reconhecida.
    - None: quando o texto não contém expressão temporal relativa reconhecida.
    """
    if not opcoes_mes:
        return None

    opcoes_parseadas = [
        (opt, ym) for opt in opcoes_mes if (ym := _parse_opcao_mes(opt)) is not None
    ]
    if not opcoes_parseadas:
        return None

    texto = _normalizar_mes(texto_usuario)
    ref = referencia or datetime.now()
    ym_atual = (ref.year, ref.month)
    ym_passado = _subtrair_meses(ref.year, ref.month, 1)

    # 1. "até o mês passado" / "até último mês"
    if re.search(r"\bate\s+(?:o\s+)?(?:mes\s+passado|ultimo\s+mes)\b", texto):
        return [opt for opt, ym in opcoes_parseadas if ym <= ym_passado]

    # 2. "até esse mês" / "até este mês" / "até o mês atual" / "até hoje"
    if re.search(r"\bate\s+(?:o\s+)?(?:(?:esse|este)\s+mes|mes\s+atual|hoje)\b", texto):
        return [opt for opt, ym in opcoes_parseadas if ym <= ym_atual]

    # 3. "últimos N meses"
    match_ultimos = re.search(r"\bultimos?\s+(\d+)\s+mes(?:es)?\b", texto)
    if match_ultimos:
        n = max(1, int(match_ultimos.group(1)))
        ym_inicio = _subtrair_meses(ref.year, ref.month, n - 1)
        return [opt for opt, ym in opcoes_parseadas if ym_inicio <= ym <= ym_atual]

    # 4. "mês passado" / "último mês" (pontual)
    if re.search(r"\b(?:mes\s+passado|ultimo\s+mes)\b", texto):
        return [opt for opt, ym in opcoes_parseadas if ym == ym_passado]

    # 5. "esse mês" / "este mês" / "mês atual" (pontual)
    if re.search(r"\b(?:(?:esse|este)\s+mes|mes\s+atual)\b", texto):
        return [opt for opt, ym in opcoes_parseadas if ym == ym_atual]

    # 6. "até <nome_do_mes>" (ex: "até outubro", "até out/2026")
    match_ate_mes = re.search(r"\bate\s+(?:o\s+mes\s+de\s+)?([a-z]+)(?:/(\d{4}))?\b", texto)
    if match_ate_mes:
        token_mes = match_ate_mes.group(1)
        ano_str = match_ate_mes.group(2)
        num_mes = _NUM_MES_POR_ABREV.get(token_mes)
        if num_mes is None:
            abrev = _MESES_PT.get(token_mes)
            if abrev:
                num_mes = _NUM_MES_POR_ABREV.get(abrev)
        if num_mes is not None:
            ano_alvo = int(ano_str) if ano_str else ref.year
            ym_alvo = (ano_alvo, num_mes)
            return [opt for opt, ym in opcoes_parseadas if ym <= ym_alvo]

    return None


def _normalizar_mes(valor: str) -> str:
    """Converte um valor para letras minúsculas sem acento, para comparação."""
    texto = unicodedata.normalize("NFKD", valor.lower().strip())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def _corresponde_mes(candidato: str, opcao: str) -> bool:
    """
    Verifica se 'candidato' (vindo da IA) bate com 'opcao' (vinda do filtro).

    Exemplos:
      candidato='out/2024', opcao='out/2024' -> True
      candidato='outubro',  opcao='out/2024' -> True
      candidato='outubro/2024', opcao='out/2024' -> True
    """
    cand = _normalizar_mes(candidato)
    opt = _normalizar_mes(opcao)

    if cand == opt:
        return True

    # Extrai o sufixo de ano da opção (ex: '/2024')
    sufixo_ano = ""
    if "/" in opt:
        sufixo_ano = "/" + opt.split("/")[-1]  # ex: '/2024'

    # Verifica se o candidato é um nome de mês por extenso
    for nome_completo, abrev in _MESES_PT.items():
        if cand.startswith(nome_completo) or cand == abrev:
            prefixo_abrev = abrev
            if opt.startswith(prefixo_abrev + "/"):
                # Se o candidato também tem um ano, ele deve bater
                if "/" in cand:
                    cand_ano = "/" + cand.split("/")[-1]
                    return cand_ano == sufixo_ano
                # Sem ano no candidato: aceita qualquer ano
                return True

    return False


def _casar_opcoes(candidatos: list[str] | None, opcoes_disponiveis: list[str]) -> list[str] | None:
    """
    Faz o match entre os valores retornados pela IA e as opções reais do filtro.
    Retorna:
    - None: apenas se `candidatos` for None (intenção explícita de mostrar todos).
    - list[str]: opções correspondentes encontradas (pode ser [] se nada casar).
    """
    if candidatos is None:
        return None  # Sem filtro (explícito)

    resultado = []
    for opt in opcoes_disponiveis:
        for cand in candidatos:
            if _corresponde_mes(cand, opt) or _normalizar_mes(cand) in _normalizar_mes(opt) or _normalizar_mes(opt) in _normalizar_mes(cand):
                resultado.append(opt)
                break

    return resultado


class AIFilterInterpreter:
    """
    Interpreta um comando de filtro em linguagem natural usando o modelo Qwen local.
    """

    MODEL_FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"

    def __init__(self):
        self.model_path = AI_DIR / self.MODEL_FILENAME
        self._llm = None

    def _get_llm(self):
        """Carrega o modelo na primeira chamada (lazy loading)."""
        if self._llm is not None:
            return self._llm

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo de IA não encontrado em: {self.model_path}"
            )

        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python não está instalado. "
                "Execute: pip install llama-cpp-python"
            )

        num_threads = max(1, os.cpu_count() or 4)
        self._llm = Llama(
            model_path=str(self.model_path),
            n_ctx=2048,
            n_threads=num_threads,
            verbose=False,
        )
        return self._llm

    def interpretar(
        self,
        texto_usuario: str,
        opcoes_por_filtro: dict[str, list[str]],
    ) -> dict[str, list[str] | None]:
        """
        Interpreta o texto do usuário e retorna o estado de filtros desejado.

        Parâmetros:
            texto_usuario:    O que o usuário digitou na barra de IA.
            opcoes_por_filtro: Dicionário {chave: [opcao1, opcao2, ...]} com as
                               opções atualmente disponíveis em cada filtro do
                               dashboard (ex: {"mes": ["jan/2024", "fev/2024"], ...}).

        Retorno:
            Dicionário {chave: lista_selecionada | None}.
            - None significa "sem filtro nessa chave" (seleciona tudo).
            - Uma lista significa que somente esses valores devem ser selecionados.
            Chaves ausentes no retorno = filtro não alterado.

        Lança:
            FileNotFoundError: se o modelo não existir.
            ImportError: se llama-cpp-python não estiver instalado.
            RuntimeError: se o modelo retornar uma resposta inválida.
        """
        agora = datetime.now()
        meses_deterministicos = (
            _resolver_meses_relativos(
                texto_usuario,
                opcoes_por_filtro.get("mes", []),
                referencia=agora,
            )
            if "mes" in opcoes_por_filtro
            else None
        )

        llm = self._get_llm()

        # Monta a representação das opções disponíveis e contexto temporal para o prompt
        opcoes_str = json.dumps(opcoes_por_filtro, ensure_ascii=False, indent=2)

        mes_atual_fmt = _mes_ano_formatado(agora.year, agora.month)
        if agora.month == 1:
            mes_passado_fmt = _mes_ano_formatado(agora.year - 1, 12)
        else:
            mes_passado_fmt = _mes_ano_formatado(agora.year, agora.month - 1)
        data_atual_str = agora.strftime("%d/%m/%Y")

        prompt = f"""<|im_start|>system
Você é um assistente especializado em filtros de dashboard de vendas.

Contexto temporal atual:
- Data de hoje: {data_atual_str}
- Mês atual: {mes_atual_fmt}
- Mês passado: {mes_passado_fmt}

O dashboard possui os seguintes filtros e suas opções disponíveis:
{opcoes_str}

Sua tarefa: interpretar o comando do usuário e retornar um JSON indicando quais valores selecionar em cada filtro.

REGRAS:
1. Retorne APENAS um objeto JSON válido, sem texto adicional.
2. Inclua apenas as chaves que o usuário quer alterar.
3. Use null SOMENTE quando o usuário pedir explicitamente para mostrar tudo ou limpar/remover o filtro.
4. Use uma lista de strings para selecionar valores específicos ou intervalos (ex: "até o mês passado" deve listar todos os meses disponíveis até {mes_passado_fmt}).
5. Os valores da lista devem ser EXATAMENTE como aparecem nas opções disponíveis acima.
6. Se o usuário pedir para limpar todos os filtros, retorne {{"mes": null, "categoria": null, "produto": null, "vendedor": null, "localidade": null}}.
7. Para meses, use o formato exato das opções (ex: "jan/2026"), nunca invente valores fora da lista.

EXEMPLOS:
Usuário: "mostra só o mês de outubro"
Resposta: {{"mes": ["out/2026"]}}

Usuário: "mostra só o mês passado"
Resposta: {{"mes": ["{mes_passado_fmt}"]}}

Usuário: "filtra as vendas até o mês passado" (com opções de jan/2026 a nov/2026 e mês passado out/2026)
Resposta: {{"mes": ["jan/2026", "fev/2026", "mar/2026", "abr/2026", "mai/2026", "jun/2026", "jul/2026", "ago/2026", "set/2026", "out/2026"]}}

Usuário: "vendas de março até junho"
Resposta: {{"mes": ["mar/2026", "abr/2026", "mai/2026", "jun/2026"]}}

Usuário: "filtra por categoria Construção"
Resposta: {{"categoria": ["Construcao"]}}

Usuário: "limpa todos os filtros"
Resposta: {{"mes": null, "categoria": null, "produto": null, "vendedor": null, "localidade": null}}
<|im_end|>
<|im_start|>user
{texto_usuario}
<|im_end|>
<|im_start|>assistant
"""

        output = llm(
            prompt,
            max_tokens=512,
            temperature=0.0,
            stop=["<|im_end|>", "```"],
        )

        raw_text = output["choices"][0]["text"].strip()

        # Extrai o JSON da resposta (pode vir com texto antes/depois)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            if meses_deterministicos:
                return {"mes": meses_deterministicos}
            raise RuntimeError(
                f"IA não retornou um JSON válido. Resposta recebida: {raw_text!r}"
            )

        try:
            resultado_bruto: dict = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            if meses_deterministicos:
                return {"mes": meses_deterministicos}
            raise RuntimeError(
                f"JSON inválido na resposta da IA: {exc}. Resposta: {raw_text!r}"
            ) from exc

        # Valida e faz o match das opções reais
        resultado_final: dict[str, list[str] | None] = {}
        chaves_validas = set(opcoes_por_filtro.keys())

        for chave, valor in resultado_bruto.items():
            if chave not in chaves_validas:
                continue  # Ignora chaves desconhecidas

            if valor is None:
                resultado_final[chave] = None
            elif isinstance(valor, list):
                opcoes = opcoes_por_filtro.get(chave, [])
                casados = _casar_opcoes([str(v) for v in valor], opcoes)
                # Se nenhuma opção real correspondeu, não converte em None (que apagaria o filtro)
                if casados:
                    resultado_final[chave] = casados
            # Ignora tipos inesperados

        # Regras temporais determinísticas têm prioridade sobre a interpretação de 'mes' do modelo
        if meses_deterministicos is not None:
            if meses_deterministicos:
                resultado_final["mes"] = meses_deterministicos
            else:
                resultado_final.pop("mes", None)

        return resultado_final
