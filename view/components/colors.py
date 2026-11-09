from PySide6.QtGui import QColor

# Modo escuro
class TemaEscuro:
    """
    Classe que define as cores do tema escuro para a aplicação.
    """
    FUNDO_PRINCIPAL = QColor("#1A1C2A")
    FUNDO_CARD = QColor("#070C27")

    DESTAQUE_PRINCIPAL = QColor("#62F59F")  
    DESTAQUE_SECUNDARIO = QColor("#47806d")  

    #TODO: adicionar cores alternativas para mais séries

    TEXTO_PRINCIPAL = QColor("#FFFFFF")
    TEXTO_SECUNDARIO = QColor("#9CA3AF")

    # BORDAS = QColor("#383E54")

# Modo claro
class TemaClaro:
    #TODO: Implementar cores para o modo claro.

    FUNDO_PRINCIPAL = QColor("#D8DCE5")
    FUNDO_CARD = QColor("#A7AFC2")
    
    DESTAQUE_PRINCIPAL = QColor("#46538E")  
    DESTAQUE_SECUNDARIO = QColor("#2F3562")

    #TODO: adicionar cores alternativas para mais séries

    TEXTO_PRINCIPAL = QColor("#000000")
    TEXTO_SECUNDARIO = QColor("#545557")

    # BORDAS = QColor("#383E54")

# Exemplo de uso:
# from view.components.colors import TemaEscuro, TemaClaro
# 
# tema_selecionado = None
# if tema == "escuro":
#     tema_selecionado = TemaEscuro()
# elif tema == "claro":
#     tema_selecionado = TemaClaro()
# 
# tema_selecionado.FUNDO_PRINCIPAL  # Acessando a cor de fundo principal do tema selecionado