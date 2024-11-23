from fastapi import FastAPI
from app.routes import predict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routes from the example module
app.include_router(predict.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}
