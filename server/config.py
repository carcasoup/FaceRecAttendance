import os

# Корень папки server
SERVER_ROOT = os.path.abspath(os.path.dirname(__file__))
# Путь к SQLite-базе
DATABASE_PATH = os.path.join(SERVER_ROOT, 'attendance.db')
DATABASE_URL  = f"sqlite:///{DATABASE_PATH}"  # например sqlite:///.../server/attendance.db

# Папка для хранения снимков студентов (parallel to models)
STUDENTS_DIR = os.path.join(SERVER_ROOT, 'students_images')