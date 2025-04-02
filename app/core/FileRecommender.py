from app.database.Keyword import Keyword
import logging

logging.basicConfig(filename='logs/recommender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileRecommender:
    def __init__(self, db):
        self.files_db = db
        self.log = logging.getLogger('recommender_logger')


    def recommend_documents(self, predictions_by_term):
      print('----------------------------- Testing Predictions ----------------------------')

      if len(predictions_by_term.items()) == 0:
        print("No term_id predicted for the file, therefore no documents to recommend")
        return
      
      docs_recommendatio_by_term = {}

      for term_id, final_prediction in predictions_by_term.items():
        term_recommended_docs = self.recommend_documents_for_term(term_id)
        docs_recommendatio_by_term[term_id] = term_recommended_docs
        
        print(f"Term: {term_id}, Recommended Documents: {term_recommended_docs}")
        self.log.info(f"Term: {term_id}, Recommended Documents:  {term_recommended_docs}")

      return docs_recommendatio_by_term

    def recommend_documents_for_term(self, term_id):
      '''
      Recommends documents based on the term_id
      '''
      keyword_table_db = Keyword(self.files_db)

      return keyword_table_db.get_file_ids_by_keyword_id(term_id, 5)