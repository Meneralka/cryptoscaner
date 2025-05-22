import uvicorn

from api import App

app_instance = App()
app = app_instance.get_app()


if __name__ == '__main__':
    uvicorn.run('api.main:app', port=8000, host='0.0.0.0', reload=True)