from fastapi import FastAPI
from app.routes import predict
from fastapi.middleware.cors import CORSMiddleware
import spacy

# Load the spacy model
spacy.cli.download("en_core_web_md")

app = FastAPI()

origins = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
    'https://prediction-app-a3xn.onrender.com'
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
