from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.api.v1.router_page import router as router_page
from app.api.v1.router_socket import router as router_socket

app = FastAPI()

# Подключаем папку со статическими файлами
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router_page)
app.include_router(router_socket)
