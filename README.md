# Face Recognition Attendance System

**Проект:** Система учёта посещаемости на основе распознавания лиц  
**Стек:** Python, FastAPI, Flask, SQLAlchemy, OpenCV, FAISS, SQLite

## Ключевые возможности
- **Детекция лиц** с помощью MTCNN (facenet-pytorch)  
- **Генерация эмбеддингов** через ResNet-50 (pretrained VGGFace2)  
- **Поиск в FAISS** (IndexFlatL2) и порог L2-расстояния для меток  
- **Автоматический сбор эмбеддингов** при загрузке фото через `/api/collect`  
- **Распознавание live** через `/api/recognize`  
- **Ручная отметка** `/api/mark`  
- **Web UI** на Flask для просмотра первой отметки входа (GMT+3)

## Быстрый запуск
1. **Клонировать репозиторий** и перейти в каталог:
   ```bash
   git clone <repo_url>
   cd FaceRecAttendance
   ```
2. **Создать виртуальное окружение** и установить зависимости:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Запустить сервер**:

4. **Открыть браузер**:
   - UI: http://localhost:8000/

## Использование API
- **POST /api/collect**  
  `multipart/form-data`: `file=@photo.jpg`, `class_name=Class101`  
  → сохраняет фото и обновляет эмбеддинги.

- **POST /api/recognize**  
  `multipart/form-data`: `file=@frame.jpg`, `class_name=Class101`  
  → возвращает список распознанных лиц.

- **POST /api/mark**  
  `x-www-form-urlencoded`: `student_name=Ivanov_Ivan`, `classroom=Class101`  
  → ручная отметка входа.

## Структура проекта
```
FaceRecAttendance/
├── client/            # CLI-скрипты OpenCV
├── server/            # FastAPI + модуль распознавания + Flask Web UI
├── requirements.txt
└── .gitignore
```
