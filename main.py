import sys
import random
import darkdetect
from PySide6 import QtCore, QtWidgets, QtGui

from config.locales import languages
from view.home import Home
from view.settings import Settings
from view.loading import Loading
from view.testeIA import Test #Testes, possivelmente apagar depois
from view.dashboard import Dashboard
from view.components.sidebar import Sidebar
from view.components.titlebar import Titlebar

from config.paths import IMAGES_DIR, FONTS_DIR, STYLE_PATH
from controller.ai_filter_thread import AIFilterThread
from model.services.ai_filter_interpreter import AIFilterInterpreter

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")

        # Instância única do interpreter de IA (mantém o modelo em memória entre chamadas)
        self._ai_interpreter = AIFilterInterpreter()
        # Referência à thread em andamento (evita garbage collection prematura)
        self._ai_thread: AIFilterThread | None = None

        #Instancia o QSettings
        self.settings = QtCore.QSettings("TCC", "Plotter")

        #Cria o stack de paginas
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored
        )
        #Instancia as outras telas
        self.homePage = Home()
        self.settingsPage = Settings()
        self.loadingPage = Loading()
        self.dashboardPage = Dashboard()

        #Esconde a barra de título e cria uma variavel pra armazenar a posição do mouse
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.old_pos = None

        #Cria o layout principal da janela
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        #Instancia a barra de titulo
        self.titlebar = Titlebar(self)
        
        #Adiciona a barra e o conteudo ao layout principal
        self.main_layout.addWidget(self.titlebar)

        #Criação do botão do menu lateral
        self.btnMenu = QtWidgets.QPushButton(self)
        self.btnMenu.setIcon(QtGui.QIcon(f"{IMAGES_DIR}/menu-burger.svg"))
        self.btnMenu.setObjectName("btnMenu")
        self.btnMenu.setFixedSize(50, 45)
        self.btnMenu.move(10, 54)
        self.btnMenu.setCursor(QtCore.Qt.PointingHandCursor)

        #Instancia o menu lateral
        self.sidebar = Sidebar(self)
        self.sidebar.setGeometry(0, 44, 0, self.height() - 44)
        
        #Conecta os botões e sinais às respectivas funções
        self.btnMenu.clicked.connect(self.sidebar.toggle_menu)
        self.sidebar.animation_started.connect(self.on_sidebar_started)
        self.sidebar.animation_finished.connect(self.on_sidebar_finished)
        self.sidebar.change_page.connect(self.change_screen)
        self.sidebar.ai_prompt.connect(self.on_ai_prompt)

        #Adiciona as paginas ao stack
        self.stack.addWidget(self.homePage)
        self.stack.addWidget(self.settingsPage)
        self.stack.addWidget(self.loadingPage)
        self.stack.addWidget(self.dashboardPage)

        #Adiciona o stack ao layout da main
        self.main_layout.addWidget(self.stack)

        #Empurra o elemento pra camada mais alta. Como o sidebar e o botão menu são elementos flutuantes (não estão em um layout), é necessario empurra-los para frente
        self.sidebar.raise_()
        self.btnMenu.raise_()

        #Recebe o sinal do arquivo "settings" e conecta à função de mundaça de tema
        self.settingsPage.theme_changed.connect(self.apply_theme)
        #Recebe o sinal do "settings" e conecta à função de mudar idioma
        self.settingsPage.language_changed.connect(self.on_language_change)
        #Recebe o sinal do "settings" para mudar a tela de volta à home
        self.settingsPage.back.connect(self.change_screen)
        #Recebe o sinal do "home" e conecta à função de começar o loading
        self.homePage.file_selected.connect(self.start_loading)
        #Recebe o sinal do "loading" e conecta à função de mudar de pagina
        self.loadingPage.finished.connect(self.change_screen)

        #Criação de uma variável para guardar a tela anterior
        self.previous_screen = 0

        saved_theme = self.settings.value("theme", "dark")
        self.apply_theme(saved_theme)
        self.load_initial_language()


    #Função para recalcular e reajustar layouts, tamanho e posições de elementos que não estão em um layout
    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"):
            self.sidebar.setFixedHeight(self.height() - 44)

        self.update_qss()

    #Função para atualizar o qss de acordo com o tamanho da tela
    def update_qss(self):
        mode = "maximized" if self.isMaximized() else "normal"
        self.setProperty("mode", mode)
    
        app = QtWidgets.QApplication.instance()
        if app:
            app.style().unpolish(app)
            app.style().polish(app)

        for child in self.findChildren(QtWidgets.QWidget):
            child.style().unpolish(child)
            child.style().polish(child)

        if hasattr(self, "stack") and self.stack.currentWidget():
            layout = self.stack.currentWidget().layout()
            if layout:
                layout.invalidate()
                layout.activate()

    #Funções para mostrar e esconder o botão do menu lateral
    def on_sidebar_started(self, abrir: bool):
        if abrir:
            self.btnMenu.hide()

    def on_sidebar_finished(self, abrir: bool):
        if not abrir:
            if self.stack.currentIndex() == 0:  # Só reexibe o btnMenu se estiver na Home
                self.btnMenu.show()
                self.btnMenu.raise_()

    #Função para mudar a tela
    def change_screen(self, indice: int = None):
        if indice is None:
            indice = self.previous_screen

        if indice == 1: #Settings
            self.previous_screen = self.stack.currentIndex()

        self.stack.setCurrentIndex(indice)

        if indice == 0:  #Home
            self.sidebar.set_mode("home")
            self.stack.setContentsMargins(0, 0, 0, 0)
            self.btnMenu.show()
            self.btnMenu.raise_()

        elif indice == 3:  #Dashboard
            self.btnMenu.hide()
            self.sidebar.set_mode("dashboard")
            self.sidebar.setGeometry(0, 44, 225, self.height() - 44)
            #Empurra o QStackedWidget 240px para a direita para a sidebar não cobrir o dashboard
            self.stack.setContentsMargins(225, 0, 0, 0)

        else:  #Settings ou Loading
            self.sidebar.hide()
            self.btnMenu.hide()
            self.stack.setContentsMargins(0, 0, 0, 0)

    #Função para mudar o tema do aplicativo
    def apply_theme(self, theme: str):
        self.settings.setValue("theme", theme)
        app = QtWidgets.QApplication.instance()

        if theme == "system":
            theme_real = "dark" if darkdetect.isDark() else "light"
        else:
            theme_real = theme

        theme_name = (f"{STYLE_PATH}/dark.qss" if theme_real == "dark" else f"{STYLE_PATH}/light.qss")

        with open(f"{STYLE_PATH}/style.qss", "r") as f:
            base_style = f.read()
        with open(theme_name, "r") as f:
            theme_style = f.read()

        #Concatenação dos arquivos .qss
        app.setStyleSheet(base_style + "\n" + theme_style)

        if hasattr(self, "settingsPage"):
            self.settingsPage.sync_theme_buttons(theme)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    #Funções para alterar o idioma do aplicativo
    def load_initial_language(self):
        saved_lang = self.settings.value("language", "pt_BR")
        self.apply_language(saved_lang)

    def on_language_change(self, lang_code: str):
        self.settings.setValue("language", lang_code)
        self.apply_language(lang_code)

    def apply_language(self, lang_code: str):
        self.sidebar.retranslate(lang_code)
        self.settingsPage.retranslate(lang_code)
        self.homePage.retranslate(lang_code)
        self.loadingPage.retranslate(lang_code)

    def start_loading(self, file_path: str):
        self.loadingPage.reset()
        self.change_screen(2)

        print(f"Iniciando análise de planilha: {file_path}") #Só para testar
        current_lang = self.settings.value("language", "pt_BR")

        self.teste = Test(file_path, current_lang)
        self.teste.started_steps.connect(self.loadingPage.setup_etapas)
        self.teste.step_changed.connect(self.loadingPage.on_step_changed)
        self.teste.failed.connect(self.loadingPage.on_failed)
        self.teste.start()

    # -------------------------------------------------------------------------
    # Interpretação de filtros por IA
    # -------------------------------------------------------------------------

    def on_ai_prompt(self, texto: str):
        """
        Disparado quando o usuário envia um comando para a IA na sidebar.
        Coleta as opções disponíveis nos filtros do dashboard ativo e
        delega a interpretação para AIFilterThread (roda no background).
        """
        # Só funciona quando o dashboard está ativo e carregado
        if self.stack.currentIndex() != 3:
            return
        if self.dashboardPage.controller is None:
            return

        controller = self.dashboardPage.controller

        # Monta o dicionário de opções disponíveis em cada filtro
        opcoes_por_filtro: dict[str, list[str]] = {}
        for chave, (card_filtro, _) in controller._filtros.items():
            # obter_selecionados() retorna None (todos) ou lista; precisamos
            # das opções completas, não das selecionadas. CardFiltro expõe
            # o dropdown interno com as opções através de obter_todas_opcoes().
            opcoes = card_filtro.obter_todas_opcoes()
            if opcoes:
                opcoes_por_filtro[chave] = opcoes

        if not opcoes_por_filtro:
            self.sidebar.set_ai_feedback("Nenhum filtro disponível no dashboard.")
            return

        if self._ai_thread is not None and self._ai_thread.isRunning():
            return

        # Bloqueia o campo de IA para evitar envios duplos
        self.sidebar.set_ai_loading(True)

        # Cria e inicia a thread
        self._ai_thread = AIFilterThread(
            texto=texto,
            opcoes_por_filtro=opcoes_por_filtro,
            interpreter=self._ai_interpreter,
            parent=self,
        )
        self._ai_thread.concluido.connect(self._on_ai_concluido)
        self._ai_thread.falhou.connect(self._on_ai_falhou)
        self._ai_thread.start()

    def _on_ai_concluido(self, resultado: dict):
        """
        Aplica os filtros interpretados pela IA ao dashboard ativo.
        'resultado' é um dicionário {chave: lista_de_valores | None}.
        """
        self.sidebar.set_ai_loading(False)

        if self.dashboardPage.controller is None:
            return

        controller = self.dashboardPage.controller
        filtros = controller._filtros
        alguma_alteracao = False

        for chave, valores in resultado.items():
            if chave not in filtros:
                continue
            card_filtro, _ = filtros[chave]
            card_filtro.definir_selecao(valores)
            alguma_alteracao = True

        if alguma_alteracao:
            controller.atualizar_por_filtros()

        # Feedback textual resumido
        if resultado:
            partes = []
            for chave, valores in resultado.items():
                if valores is None:
                    partes.append(f"{chave}: todos")
                else:
                    partes.append(f"{chave}: {', '.join(valores)}")
            self.sidebar.set_ai_feedback(" | ".join(partes))
        else:
            self.sidebar.set_ai_feedback("Nenhum filtro correspondente encontrado.")

    def _on_ai_falhou(self, mensagem: str):
        """Exibe uma mensagem de erro amigável na sidebar quando a IA falha."""
        self.sidebar.set_ai_loading(False)
        print(f"[AIFilter] Erro: {mensagem}")
        if "não encontrado" in mensagem.lower() or "filenotfounderror" in mensagem.lower():
            self.sidebar.set_ai_feedback("Modelo de IA não encontrado.")
        elif "importerror" in mensagem.lower():
            self.sidebar.set_ai_feedback("llama-cpp-python não instalado.")
        else:
            self.sidebar.set_ai_feedback("Não entendi o filtro. Tente novamente.")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtGui.QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Regular.ttf")
    QtGui.QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Bold.ttf")

    widget = Window()
    widget.resize(1200, 750)
    widget.show()

    sys.exit(app.exec())