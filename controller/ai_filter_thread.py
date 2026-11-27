"""
Thread para executar a interpretação de filtros por IA sem travar a UI.

Como o modelo roda no CPU e pode levar alguns segundos, o AIFilterThread
executa a chamada ao AIFilterInterpreter em uma QThread separada e emite
sinais para notificar a UI quando terminar.

Sinais emitidos:
  concluido(dict)  — interpretação bem-sucedida; payload = {chave: lista|None}
  falhou(str)      — erro durante a interpretação; payload = mensagem de erro
"""

from PySide6 import QtCore

from model.services.ai_filter_interpreter import AIFilterInterpreter


class AIFilterThread(QtCore.QThread):
    """QThread que roda AIFilterInterpreter.interpretar() de forma assíncrona."""

    # Emitido quando a IA interpretou o texto com sucesso
    concluido = QtCore.Signal(dict)
    # Emitido quando ocorre qualquer erro (modelo ausente, JSON inválido, etc.)
    falhou = QtCore.Signal(str)

    def __init__(
        self,
        texto: str,
        opcoes_por_filtro: dict,
        interpreter: AIFilterInterpreter | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.texto = texto
        self.opcoes_por_filtro = opcoes_por_filtro
        # Permite reutilizar um interpreter já carregado (modelo em memória)
        self._interpreter = interpreter or AIFilterInterpreter()

    def run(self):
        """Executado na thread secundária."""
        try:
            resultado = self._interpreter.interpretar(
                self.texto,
                self.opcoes_por_filtro,
            )
            self.concluido.emit(resultado)
        except Exception as exc:
            self.falhou.emit(str(exc))
