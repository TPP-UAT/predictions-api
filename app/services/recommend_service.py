import os
from typing import List
from fastapi import File, HTTPException, UploadFile
from app.services.predict import PredictService
from app.core.FileRecommender import FileRecommender
from app.database.Database import Database

# Initialize the database
# db_url = os.getenv('DB_URL')
db_url = "postgresql://user:password@localhost:5432/UAT_IA"
print("DB URL:", db_url)
database = Database(db_url)
engine = database.get_engine()
connection = engine.connect()
database.init_db()

class RecommendService:
    @staticmethod
    async def recommend_files(files: List[UploadFile] = File(...)):
        
        try:
            predictions = await PredictService.predict_files(files)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")
        
        recommendations = []

        for prediction in predictions:
            print("Recommending for file: ", prediction)
            recommender = FileRecommender(database)
            recommended_docs = recommender.recommend_documents(prediction["predictions"])

            file_recomendations = {
                "filename": prediction["filename"],
                "recommendations": recommended_docs
            }

            recommendations.append(file_recomendations)
            
        return recommendations
        