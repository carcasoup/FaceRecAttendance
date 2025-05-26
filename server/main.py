import os
import uvicorn
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

from server.db import engine, Base
from server.api import router as api_router
from server.flask_site import create_app

# Создаём таблицы перед стартами Flask и FastAPI
Base.metadata.create_all(bind=engine)

app = FastAPI(title='Face Recognition Attendance')
# API под /api
app.include_router(api_router, prefix='/api')
# Монтируем Flask-интерфейс на корень
flask_app = create_app()
app.mount('/', WSGIMiddleware(flask_app))

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 80))
    uvicorn.run('server.main:app', host=host, port=port, reload=True)