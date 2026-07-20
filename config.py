# config.py

import os

TOKEN = "8897979167:AAGOQt3SPRQWMux1q684hkAzG1Puy9WvDcE"

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
TEMP_DIR = os.path.join(BASE_DIR, "temp_charts")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# Создаём папки
for dir_path in [EXPORT_DIR, TEMP_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)