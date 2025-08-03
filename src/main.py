from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def handle_get_home():
    return 200
