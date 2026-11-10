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

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #Instancia o QSettings
        self.settings = QtCore.QSettings("TCC", "Plotter")

        #Cria o stack de paginas
        self.stack = QtWidgets.QStackedWidget()
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

        #Instancia o menu lateral
        self.sidebar = Sidebar(self)
        self.sidebar.setGeometry(0, 44, 0, self.height() - 44)
        
        #Conecta os botões e sinais às respectivas funções
        self.btnMenu.clicked.connect(self.sidebar.toggle_menu)
        self.sidebar.animation_started.connect(self.on_sidebar_started)
        self.sidebar.animation_finished.connect(self.on_sidebar_finished)
        self.sidebar.change_page.connect(self.change_screen)

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

        #Faz com que o cursor fique com o dedinho nos botões
        buttons = [self.btnMenu, self.sidebar.btnCloseSidebar, self.sidebar.btnConfig, self.sidebar.btnHistory]
        for btn in buttons:
            btn.setCursor(QtCore.Qt.PointingHandCursor)

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
            if self.stack.currentIndex() != 1:
                self.btnMenu.show()
                self.btnMenu.raise_()

    #Função para mudar a tela
    def change_screen(self, indice: int):
        self.stack.setCurrentIndex(indice)

        if indice in (1, 2):
            self.sidebar.hide()
            self.btnMenu.hide()
        else:
            self.btnMenu.show()
            self.btnMenu.raise_()

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

    #Funções para alterar o idioma do aplicativo
    def load_initial_language(self):
        saved_lang = self.settings.value("language", "pt_BR")
        self.apply_language(saved_lang)

    def on_language_change(self, lang_code: str):
        self.settings.setValue("language", lang_code)
        self.apply_language(lang_code)

    def apply_language(self, lang_code: str):
        self.settingsPage.retranslate(lang_code)
        self.homePage.retranslate(lang_code)
        self.loadingPage.retranslate(lang_code)

        texts = languages.get(lang_code, languages["pt_BR"])
        self.sidebar.btnHistory.setText(texts["menu_dashboard"])
        self.sidebar.btnConfig.setText(texts["menu_settings"])

    def start_loading(self, file_path: str):
        self.change_screen(2)

        print(f"Iniciando análise de planilha: {file_path}") #Só para testar
        current_lang = self.settings.value("language", "pt_BR")

        self.teste = Test(file_path, current_lang)
        self.teste.started_steps.connect(self.loadingPage.setup_etapas)
        self.teste.step_changed.connect(self.loadingPage.on_step_changed)
        self.teste.failed.connect(self.loadingPage.on_failed)
        self.teste.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtGui.QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Regular.ttf")
    QtGui.QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Bold.ttf")

    widget = Window()
    widget.resize(1000, 650)
    widget.show()

    sys.exit(app.exec())