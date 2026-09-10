from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


ASSETS_DIR = ROOT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
STYLE_PATH = ASSETS_DIR / "style.qss"

CONTROLLER_DIR = ROOT_DIR / "controller"

MODELS_DIR = ROOT_DIR / "model"

VIEWS_DIR = ROOT_DIR / "view"