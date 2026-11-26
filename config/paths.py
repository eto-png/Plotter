from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# visuais
ASSETS_DIR = ROOT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
STYLE_PATH = ASSETS_DIR / "style"

# dados
DATA_DIR = ROOT_DIR / "data"
DASHBOARDS_DIR = DATA_DIR / "dashboards"
SCHEMA_DIR = DATA_DIR / "schema"
SHEETS_DIR = DATA_DIR / "sheets"

#ia
AI_DIR = ROOT_DIR / "ai"

# estáticos
STATIC_DIR = ROOT_DIR / "static"
DASHBOARD_MODELS_DIR = STATIC_DIR / "dashboard_models"

