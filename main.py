from fastapi import FastAPI
from neoapp.app.api.endpoints.api import router as api_router 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Подключение маршрутизатора с эндпоинтами к приложению
app.include_router(api_router)

app.mount("/static", StaticFiles(directory="neoapp/front/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open(r"neoapp\front\teamplates\Login.html", "r",encoding="utf-8", errors="ignore") as file:
        html_content = file.read()
    return html_content

@app.get("/employee", response_class=HTMLResponse)
async def get_page1():
    with open(r"neoapp\front\teamplates\employee.html", "r",encoding="utf-8", errors="ignore") as file:
        html_content = file.read()
    return html_content

@app.get("/request", response_class=HTMLResponse)
async def get_page2():
    with open(r"neoapp\\front\\teamplates\\request_details.html", "r",encoding="utf-8", errors="ignore") as file:
        html_content = file.read()
    return html_content


# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)