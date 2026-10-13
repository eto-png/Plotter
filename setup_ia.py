import os
import urllib.request
from pathlib import Path
from config.paths import ROOT_DIR, AI_DIR

# Configuração da URL do modelo (Recomendado para uso em CPU: Phi-3-Mini quantizado)
MODEL_URL = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
MODEL_FILENAME = "phi-3-mini-4k-instruct-q4.gguf"

# Utiliza pathlib para garantir caminhos absolutos baseados na raiz do projeto

MODEL_PATH = AI_DIR / MODEL_FILENAME

def download_progress(count, block_size, total_size):
    """Exibe uma barra de progresso simples no terminal."""
    percent = int(count * block_size * 100 / total_size)
    # Limita a 100% caso o cálculo passe minimamente
    percent = min(percent, 100)
    print(f"\rBaixando modelo de I.A. offline... {percent}% concluído", end="")

def setup_ia():
    print("--- Assistente de Configuração de I.A. do Plotter ---")
    
    # Cria as pastas assets/ e assets/models automaticamente se não existirem
    AI_DIR.mkdir(parents=True, exist_ok=True)
    
    if MODEL_PATH.exists():
        print(f"\n[OK] O modelo já está instalado em: {MODEL_PATH}")
        print("Nenhum download necessário. O ambiente está pronto para rodar offline!")
    else:
        print(f"\n[AVISO] Modelo não encontrado na pasta {AI_DIR}")
        print(f"Iniciando o download de {MODEL_FILENAME} (Aprox. 2.4 GB)...")
        print("Isso pode demorar alguns minutos dependendo da sua conexão.\n")
        
        try:
            # Baixa o arquivo do Hugging Face e salva no destino
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=download_progress)
            print(f"\n\n[SUCESSO] Modelo baixado e salvo com sucesso em: {MODEL_PATH}")
        except Exception as e:
            print(f"\n\n[ERRO] Falha ao baixar o modelo. Verifique sua internet. Detalhes: {e}")
            # Limpa o arquivo corrompido caso o download seja interrompido
            if MODEL_PATH.exists():
                os.remove(MODEL_PATH)

if __name__ == "__main__":
    setup_ia()