import sys
import random
import time
from PySide6 import QtCore, QtWidgets, QtGui

from config.locales import languages

class Test(QtCore.QThread):
  started_steps = QtCore.Signal(list)
  step_changed = QtCore.Signal(int, int, str)
  finished_success = QtCore.Signal()
  failed = QtCore.Signal(int)

  def __init__(self, file_path, lang_code: str):
    super().__init__()
    self.file_path = file_path

    lang_data = languages.get(lang_code, languages["pt_BR"])
    self.etapas = lang_data.get("loading_steps", [])

  def run(self):
    self.started_steps.emit(self.etapas)

    try:
      # Exemplo de execução passo a passo
      for index, etapa in enumerate(self.etapas):
        # SIMULAÇÃO: Substitua pelo seu código real da IA / leitura da planilha
        time.sleep(1.5)

        percentual = int(((index + 1) / len(self.etapas)) * 100)

        # Exemplo de simulação de erro na etapa 2 (descomente para testar o erro):
        if index == 2:
          raise Exception("Falha de conexão com a API da IA no passo 3.")

        # Emite sinal para atualizar a interface
        self.step_changed.emit(index, percentual, etapa)

      self.finished_success.emit()

    except Exception:
      # Se ocorrer qualquer erro, notifica a tela
      self.failed.emit(index)