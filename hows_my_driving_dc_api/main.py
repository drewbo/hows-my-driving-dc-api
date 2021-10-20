"""hows-my-driving-dc-api main app"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    """test"""
    return {"Hello": "World"}
