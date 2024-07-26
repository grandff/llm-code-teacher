from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def post_root():
    return {"Hello": "World post"}

@app.get("/hi")
def read_hi():
    return {"Hello": "hi"}

@app.post("/hi")
def post_hi():
    return {"Hello": "hi post"}