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
    def print_predictions(self):
        print('----------------------------- Testing Predictions ----------------------------')

        if len(self.predictions) == 0:
            print("There are no predictions")

        else:
            for term_id, prediction in self.temporal_predictions.items():
                print(f"Term: {term_id}, Probability: {prediction}")
                self.log.info(f"Term: {term_id}, Probability: {prediction}")

            print('----------------------- Combined Predictions -------------------------------')

            for term_id, final_prediction in self.predictions_by_term.items():
                print(f"Term: {term_id}, Probability: {final_prediction}")
                self.log.info(f"Term: {term_id}, Probability: {final_prediction}")

    '''
    Predicts the terms for a given input creator
    '''
    def predict_terms(self, data_input):
        term_prediction = TermPredictionv2(data_input, self.thesaurus)

        # Initial term ID
        root_term = self.thesaurus.get_by_id("1")

        predicted_terms = []
        predictions = term_prediction.predict_text(predicted_terms, root_term.get_id())
        return predictions

    '''
    Combines the predictions from different input creators and generates the final prediction
    '''
    def generate_predictions(self, predictions):
        # Combine predictions from different input creators if the term is already in the predictions
        for prediction in predictions:
            if prediction.get_term() not in self.predictions:
                self.predictions[prediction.get_term()] = prediction
            else:
                probability = prediction.get_probabilities()[0]
                self.predictions[prediction.get_term()].add_probability(probability)
                self.predictions[prediction.get_term()].add_multiplier(prediction.get_multipliers()[0])
                self.predictions[prediction.get_term()].add_multiplier_name(prediction.get_multipliers_names()[0])
                self.predictions[prediction.get_term()].add_parent(prediction.get_parents()[0])

        # Generate prediction object with the final probabilities combined
        final_predictions = {}
        for term_id, prediction in self.predictions.items():
            # Get term name from thesaurus
            term_name = self.thesaurus.get_by_id(term_id).get_name()
            
            final_prediction = 0
            for pred, multiplier in zip(prediction.get_probabilities(), prediction.get_multipliers()):
                final_prediction += pred * multiplier
            final_predictions[term_id] = { 'probability': final_prediction, 'name': term_name }

        self.predictions_by_term = final_predictions

        # We want the info for the prediction for testing purposes
        for term_id, prediction in self.predictions.items():
            self.temporal_predictions[term_id] = {
                'probabilities': prediction.get_probabilities(),
                'multipliers': prediction.get_multipliers(),
                'multipliersNames': prediction.get_multipliers_names(),
                'parent': prediction.get_parents()
            }

    '''
    Extracts the abstract and full text from a file and predicts the terms
    '''
    async def predict_for_file(self, file):
        # Get the text from the file
        abstract, full_text = await get_text_from_file(file)
        summarized_text = summarize_text(full_text, 0.25, max_sentences=100, additional_stopwords={"specific", "unnecessary", "technical"})
        data_input = {"abstract": abstract, "summarize-summarize": summarized_text, "summarize-full_text": full_text}

        predictions = self.predict_terms(data_input)
        # self.generate_predictions(predictions)
        print("***************************************")
        # TESTING
        for prediction in predictions:
            print(f"Term: {prediction.get_term()}, Probability: {prediction.get_combined_probability()}, probabilites: {prediction.get_probabilities()}, multipliersNames: {prediction.get_multipliers_names()}, parent: {prediction.get_parents()}")
        # self.print_predictions()

        # Return the final predictions
        # return self.predictions_by_term
