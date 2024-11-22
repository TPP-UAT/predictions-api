from fastapi import FastAPI
from app.routes import predict

app = FastAPI()

# Include routes from the example module
app.include_router(predict.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}
