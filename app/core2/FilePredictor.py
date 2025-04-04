import os
import logging
from app.utils.UATMapper import UATMapper
from app.core2.TermPrediction import TermPredictionv2
from app.utils.articles_parser import get_text_from_file
from app.utils.summarize_text import summarize_text

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FilePredictorv2:
    def __init__(self):
        # Initialize the thesaurus
        mapper = UATMapper(os.path.abspath("app/data/UAT-filtered.json"))
        self.thesaurus = mapper.map_to_thesaurus()

        # For logging purposes
        self.log = logging.getLogger('predictor_logger')

    # TODO: Remove function after testing
    '''
    Prints the predictions in the console
    '''
    def print_predictions(self, predictions):
        if len(predictions) == 0:
            print("There are no predictions")

        else:
            for prediction in predictions:
                print(f"Term: {prediction.get_term()}, Probability: {prediction.get_combined_probability()}, probabilites: {prediction.get_probabilities()}, multipliersNames: {prediction.get_multipliers_names()}, parent: {prediction.get_parents()}")

    '''
    Predicts the terms for a given file
    '''
    def predict_terms(self, data_input):
        term_prediction = TermPredictionv2(data_input, self.thesaurus)

        # Initial term ID
        root_term = self.thesaurus.get_by_id("1")
        level = 0

        predicted_terms = []
        predictions = term_prediction.predict_text(predicted_terms, root_term.get_id(), level)
        return predictions

    '''
    Extracts the abstract and full text from a file and predicts the terms
    '''
    async def predict_for_file(self, file):
        self.log.info("\n\n")
        self.log.info(f"****** Starting prediction for file: {file.filename} ********")
        # Get the text from the file
        abstract, full_text = await get_text_from_file(file)
        summarized_text = summarize_text(full_text, 0.25, max_sentences=100, additional_stopwords={"specific", "unnecessary", "technical"})
        data_input = {"abstract": abstract, "summarize-summarize": summarized_text, "summarize-full_text": full_text}

        predictions = self.predict_terms(data_input)

        print("----------------------------- Predictions ----------------------------")
        self.print_predictions(predictions)

        # return self.predictions_by_term

    """
    Recursively collect all ancestor IDs of a given term.
    """
    def get_ancestors(self, thesaurus, term_id):
        ancestors = set()
        term = thesaurus.get_by_id(term_id)
        if not term:
            return ancestors
        for parent_id in term.get_parents():
            ancestors.add(parent_id)
            ancestors.update(self.get_ancestors(thesaurus, parent_id))
        return ancestors

    def filter_parent_terms(self, predictions, thesaurus):
        # Obtener todos los IDs de términos en las predicciones
        prediction_ids = {cp.get_term() for cp in predictions}
        
        # Recolectar todos los ancestros de cada término que están en la lista de predicciones
        ancestors_to_remove = set()
        for cp in predictions:
            term_id = cp.get_term()
            ancestors = self.get_ancestors(thesaurus, term_id)
            common_ancestors = ancestors & prediction_ids
            ancestors_to_remove.update(common_ancestors)
        
        # Filtrar las predicciones, excluyendo los ancestros
        filtered = [cp for cp in predictions if cp.get_term() not in ancestors_to_remove]
        return filtered