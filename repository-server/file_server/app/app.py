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

@app.get("/file")
def read_file():
    return {"Hello": "World from file"}

@app.post("/file")
def post_file():
    return {"Hello": "World post from file"}
