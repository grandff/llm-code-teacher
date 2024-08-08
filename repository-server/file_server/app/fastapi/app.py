from fastapi import FastAPI
from routers import file_router

app = FastAPI()

# routers
app.include_router(file_router.router)

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