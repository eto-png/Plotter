import math

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QSettings
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPainterPath, QFontDatabase

from view.components.colors import TemaEscuro, TemaClaro

from config.paths import FONTS_DIR

class BaseGrafico(QWidget):
    def __init__(self, parent=None, dados=None, titulo=""):
        super().__init__(parent)
        self.settings = QSettings("TCC", "Plotter")
        self.tema = TemaEscuro if self.settings.value("theme", "dark") == "dark" else TemaClaro()

        self.titulo = titulo
        self.fonte = "Poppins"

        self.dados = dados or []

    def atulizar_dados(self, dados_novos):
        self.dados = dados_novos
        self.update()

    def paintEvent(self, event):
        QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Regular.ttf")
        QFontDatabase.addApplicationFont(f"{FONTS_DIR}/Poppins-Bold.ttf")

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        card_rect = rect.adjusted(1, 1, -1, -1)
        tema = self.tema

        # Fundo do Card com cantos arredondados e borda sutil
        painter.setPen(QPen(QColor(0, 0, 0, 0), 1))
        painter.setBrush(QBrush(tema.FUNDO_PRINCIPAL))
        arred = 5
        painter.drawRoundedRect(card_rect, arred, arred)

        # Título do Card
        if self.titulo:
            caixa_label = QRectF(1, 0, rect.width() - 2, 28)

            #metade da altura da caixa pra poder fazer a metade de baixo sem arredondar
            metade_label = QRectF(1, 14, rect.width() - 2, 16)
            painter.setBrush(QBrush(tema.FUNDO_CARD))
            painter.drawRoundedRect(caixa_label, arred, arred)

            painter.fillRect(metade_label, tema.FUNDO_CARD)

            fonte_titulo = QFont(self.fonte, 10, QFont.Weight.Normal)
            painter.setFont(fonte_titulo)
            painter.setPen(tema.TEXTO_PRINCIPAL)
            painter.drawText(caixa_label, Qt.AlignmentFlag.AlignCenter, self.titulo)

        # Encerra o QPainter para evitar travamentos de concorrência na classe filha
        painter.end()

    def calcular_max_val_dinamico(self, valores: list) -> float:
            """
            Calcula o teto do eixo Y arredondando para a dezena, centena, milhar, etc.,
            mais próxima para cima, dependendo da ordem de grandeza do maior valor.
            """
            if not valores:
                return 10.0
    
            maior_valor = max(valores)
            if maior_valor <= 0:
                return 10.0
    
            # Quantidade de dígitos da parte inteira
            qtd_digitos = len(str(int(maior_valor)))
    
            # Define a base (2 dígitos -> 10, 3 dígitos -> 100, 4 dígitos -> 1000)
            base = 10 ** max(1, qtd_digitos - 1)
    
            # Arredonda para CIMA na base encontrada
            max_val = math.ceil(maior_valor / base) * base
    
            return float(max_val)

class LinhaDoTempo(BaseGrafico):
    def __init__(self, parent=None, dados=None, titulo=None):
        #obrigatorio que os dados sejam uma coluna de data e outra de valor
        super().__init__(parent, dados, titulo)

        self.setMinimumSize(850, 320)
        self.resize(850,320)


    def paintEvent(self, event):

        super().paintEvent(event)

        tema = self.tema

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        fonte_principal = self.fonte
        

        #area de desenho do card
        margin_left = 100
        margin_right = 50
        margin_top = 65
        margin_bottom = 45

        plot_width = rect.width() - margin_left - margin_right #largura da tela desenhavel
        plot_height = rect.height() - margin_top - margin_bottom #altura da tela desenhavel
        y_baseline = rect.height() - margin_bottom #base da tela desenhavel

        valores = [val for _, val in self.dados]

        min_val = 0.0
        max_val = self.calcular_max_val_dinamico(valores)

        #linhas intermediarias
        num_linhas = 4  # Quantidade de divisões intermediárias
        passo_valor = (max_val - min_val) / num_linhas


        # Caneta pontilhada/traçada para as linhas de fundo
        pen_grid = QPen(QColor(tema.TEXTO_SECUNDARIO), 1, Qt.PenStyle.DotLine)
        font_y_labels = QFont(fonte_principal, 8)

        for i in range(num_linhas + 1):
            valor_nivel = min_val + (i * passo_valor)
            
            # Calcula a posição Y em pixels exatamente com a mesma fórmula dos pontos
            y_linha = y_baseline - ((valor_nivel - min_val) / (max_val - min_val)) * plot_height

            # 1. Desenha a linha horizontal pontilhada de margem a margem
            painter.setPen(pen_grid)
            painter.drawLine(margin_left, y_linha, rect.width() - margin_right, y_linha)

            # 2. Escreve o valor numérico na margem esquerda (Eixo Y)
            painter.setFont(font_y_labels)
            painter.setPen(tema.TEXTO_SECUNDARIO)
            box_rotulo_y = QRectF(-10, y_linha - 10, margin_left - 10, 20)
            painter.drawText(
                box_rotulo_y, 
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 
                f"R$ {valor_nivel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        
        #calculo das cordenadas dos pontos
        n_points = len(self.dados) # numero de pontos
        step_x = plot_width / (n_points - 1) if n_points > 1 else plot_width # tamanho do intervalo horizontal entre linhas

        points = []
        for i, (mes, val) in enumerate(self.dados):
            x = margin_left + i * step_x
            y = y_baseline - ((val - min_val) / (max_val - min_val)) * plot_height
            points.append((x, y, mes, val))
        
        #bolinhas nos pontos
        painter.setBrush(QBrush(tema.DESTAQUE_PRINCIPAL))
        raio_bolinha = 3.5  # Diâmetro total de 7px

        for x, y, _, _ in points:
            painter.drawEllipse(QRectF(x - raio_bolinha, y - raio_bolinha, raio_bolinha * 2, raio_bolinha * 2))

        #gradiente
        gradient = QLinearGradient(0, margin_top, 0, y_baseline)
        gradient.setColorAt(0.0, tema.DESTAQUE_PRINCIPAL)
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        path_area = QPainterPath()
        path_area.moveTo(points[0][0], y_baseline)
        for x, y, _, _ in points:
            path_area.lineTo(x, y)
        path_area.lineTo(points[-1][0], y_baseline)
        path_area.closeSubpath()

        painter.fillPath(path_area, QBrush(gradient))


        #linha
        path_line = QPainterPath()
        path_line.moveTo(points[0][0], points[0][1])
        for x, y, _, _ in points[1:]:
            path_line.lineTo(x, y)

        pen_line = QPen(tema.DESTAQUE_PRINCIPAL, 2)
        painter.setPen(pen_line)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_line)

        #linha guia na base
        pen_axis = QPen(tema.FUNDO_PRINCIPAL, 1)
        painter.setPen(pen_axis)
        painter.drawLine(margin_left, y_baseline, rect.width() - margin_right, y_baseline)

        #rotulos
        font_labels = QFont(fonte_principal, 8)
        font_values = QFont(fonte_principal, 8)

        for i, (x, y, mes, val) in enumerate(points):
            # 1. Nome do Mês (Eixo X)
            painter.setFont(font_labels)
            painter.setPen(tema.TEXTO_PRINCIPAL)
            painter.drawText(QRectF(x - 35, y_baseline + 8, 70, 20), Qt.AlignmentFlag.AlignCenter, mes)

            # 2. Verificação de tendência: próximo ponto é mais alto?
            proximo_mais_alto = (i < len(points) - 1) and (points[i + 1][3] > val)
            
            # Se o próximo ponto subir, coloca ABAIXO da bolinha (y + 12). 
            # Caso contrário, coloca ACIMA da bolinha (y - 22).
            y_text = y + 5 if proximo_mais_alto else y - 25

            # 3. Desenho do Valor Numérico
            painter.setFont(font_values)
            painter.setPen(tema.TEXTO_PRINCIPAL)
            val_str = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            painter.drawText(QRectF(x - 30, y_text, 60, 18), Qt.AlignmentFlag.AlignCenter, val_str)

        pen_axis = QPen(tema.TEXTO_PRINCIPAL)  # Cor sutil visível no tema escuro
        painter.setPen(pen_axis)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(margin_left, y_baseline, rect.width() - margin_right, y_baseline)

class BarrasH(BaseGrafico):
    def __init__(self, parent=None, dados=None, titulo=None, max_h=0, max_w=0):
        super().__init__(parent, dados, titulo)
        self.setMinimumSize(850, 320)
        # self.resize(850, 320)

    def paintEvent(self, event):
        super().paintEvent(event)

        tema = self.tema
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        fonte_principal = self.fonte

        # Margens aumentadas na esquerda para caber os textos possivelmente longos/quebrados
        margin_left = 135
        margin_right = 50
        margin_top = 65
        margin_bottom = 45

        plot_width = rect.width() - margin_left - margin_right
        plot_height = rect.height() - margin_top - margin_bottom
        y_baseline = rect.height() - margin_bottom

        if not self.dados:
            painter.end()
            return

        valores = [val for _, val in self.dados]
        min_val = 0.0
        max_val = self.calcular_max_val_dinamico(valores)

        # --- Eixo X (Linhas Pontilhadas e Rótulos) ---
        num_linhas = 3
        passo_valor = (max_val - min_val) / num_linhas

        pen_grid = QPen(QColor(tema.TEXTO_SECUNDARIO), 1, Qt.PenStyle.DotLine)
        font_x_labels = QFont(fonte_principal, 8)
        painter.setFont(font_x_labels)

        for i in range(num_linhas + 1):
            valor_nivel = min_val + (i * passo_valor)
            x_linha = margin_left + ((valor_nivel - min_val) / (max_val - min_val)) * plot_width

            painter.setPen(pen_grid)
            painter.drawLine(x_linha, margin_top - 10, x_linha, y_baseline)

            painter.setPen(tema.TEXTO_SECUNDARIO)
            if valor_nivel >= 1000:
                val_str = f"R$ {val:,.0f} Mil".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                val_str = f"R$ {valor_nivel:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

            if valor_nivel == 0:
                val_str = "0"

            box_rotulo_x = QRectF(x_linha - 30, y_baseline + 5, 60, 20)
            painter.drawText(box_rotulo_x, Qt.AlignmentFlag.AlignCenter, val_str)

        # Linha Base Eixo Y (Vertical)
        pen_axis = QPen(tema.TEXTO_PRINCIPAL, 1)
        painter.setPen(pen_axis)
        painter.drawLine(margin_left, margin_top - 10, margin_left, y_baseline + 5)

        # --- Desenho das Barras e Rótulos do Eixo Y ---
        n_barras = len(self.dados)
        espaco_entre_barras = 20
        altura_barra = (plot_height - (espaco_entre_barras * (n_barras - 1))) / n_barras

        font_y_labels = QFont(fonte_principal, 9)
        font_valores_barra = QFont(fonte_principal, 9, QFont.Weight.Medium)

        for i, (categoria, val) in enumerate(self.dados):
            y = margin_top + (i * (altura_barra + espaco_entre_barras))
            largura = ((val - min_val) / (max_val - min_val)) * plot_width

            # 1. Rótulo Eixo Y com Quebra de Linha Inteligente
            painter.setFont(font_y_labels)
            painter.setPen(tema.TEXTO_PRINCIPAL)
            
            nome_cat = str(categoria)
            limite_caracteres = 18 # Ajuste este valor se necessário para textos maiores ou menores

            if len(nome_cat) > limite_caracteres and " " in nome_cat:
                # Encontra o último espaço antes do limite de caracteres para não cortar palavras no meio
                ponto_quebra = nome_cat[:limite_caracteres].rfind(" ")
                if ponto_quebra == -1: # Fallback se a primeira palavra for enorme
                    ponto_quebra = nome_cat.find(" ")
                
                linha1 = nome_cat[:ponto_quebra]
                linha2 = nome_cat[ponto_quebra+1:]
                
                # Desenha a primeira linha deslocada levemente para cima
                box_cat_L1 = QRectF(0, y - 6, margin_left - 10, altura_barra)
                painter.drawText(box_cat_L1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, linha1)
                
                # Desenha a segunda linha deslocada levemente para baixo
                box_cat_L2 = QRectF(0, y + 8, margin_left - 10, altura_barra)
                painter.drawText(box_cat_L2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, linha2)
            else:
                # Comportamento padrão (uma linha)
                box_categoria = QRectF(0, y, margin_left - 10, altura_barra)
                painter.drawText(box_categoria, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, nome_cat)

            # 2. Gradiente Horizontal
            gradient = QLinearGradient(margin_left, 0, margin_left + largura, 0)
            gradient.setColorAt(0.0, QColor(92, 255, 141))
            gradient.setColorAt(1.0, tema.DESTAQUE_PRINCIPAL)

            # 3. Retângulo da Barra
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            barra_rect = QRectF(margin_left, y, largura, altura_barra)
            painter.drawRect(barra_rect)

            # 4. Valor Numérico Dentro da Barra
            painter.setFont(font_valores_barra)
            painter.setPen(tema.TEXTO_PRINCIPAL)
            
            if val >= 1000:
                val_barra_str = f"R$ {val / 1000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                val_barra_str = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
            box_valor_barra = QRectF(margin_left, y, largura - 10, altura_barra)
            painter.drawText(box_valor_barra, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, val_barra_str)

        painter.end()