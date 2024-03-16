from fastapi import FastAPI
from neoapp.app.api.endpoints.api import router as api_router 

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Подключение маршрутизатора с эндпоинтами к приложению
app.include_router(api_router)



# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)