from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from server.config import DATABASE_URL

# Настройка движка и сессий
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
# Единый Base для всех моделей
Base = declarative_base()