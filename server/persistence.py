import os
import json
import faiss
import joblib
from server.config import MODEL_DIR, INDEX_PATH, LABEL_MAP_PATH

def save_model(index, label_map):
    """
    Сохраняет FAISS-индекс и отображение меток в файлы.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(LABEL_MAP_PATH, 'w') as f:
        json.dump(label_map, f)
    print(f"[INFO] Модель сохранена в {INDEX_PATH}, метки — в {LABEL_MAP_PATH}")

def load_model():
    """
    Загружает FAISS-индекс и отображение меток, если они существуют.
    Возвращает (index, label_map) или (None, {}) если не найдено.
    """
    if os.path.exists(INDEX_PATH) and os.path.exists(LABEL_MAP_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(LABEL_MAP_PATH) as f:
            label_map = json.load(f)
        print(f"[INFO] Модель загружена из {INDEX_PATH}")
        return index, label_map
    print("[INFO] Индекс или словарь меток не найдены, возвращаю пустые значения")
    return None, {}
