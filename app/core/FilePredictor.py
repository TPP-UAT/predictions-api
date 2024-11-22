import logging
from app.core.TermPrediction import TermPrediction
from app.utils.articles_parser import get_text_from_file

logging.basicConfig(filename='logs/predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FilePredictor:
    def __init__(self, initial_term_id, thesaurus):
        self.initial_term_id = initial_term_id
        self.input_creators = ['abstract', 'normal', 'tf-idf']
        self.predictions = {}
        self.predictions_by_term = {}
        self.thesaurus = thesaurus
        self.log = logging.getLogger('predictor_logger')

    '''
    Prints the predictions in the console
    '''
    def print_predictions(self):
        print('----------------------------- Predictions ----------------------------')

        if len(self.predictions) == 0:
            print("There are no predictions")

        else:
            for term_id, prediction in self.predictions.items():
                term_obj = self.thesaurus.get_by_id(term_id)
                parents = term_obj.get_parents()
                print(f"Term: {term_id}, Probabilities: {prediction.get_probabilities()}, Multipliers: {prediction.get_multipliers()}, Parents: {parents}")

            for term_id, final_prediction in self.predictions_by_term.items():
                print(f"Term: {term_id}, Probability: {final_prediction}")

    '''
    Predicts the terms for a given input creator
    '''
    def predict_terms(self, input_creator, text):
        term_prediction = TermPrediction(input_creator)

        predicted_terms = []
        predictions = term_prediction.predict_texts(text, self.initial_term_id, predicted_terms)
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

        # Generate prediction object with the final probabilities
        final_predictions = {}
        for term_id, prediction in self.predictions.items():
            final_prediction = 0
            for pred, multiplier in zip(prediction.get_probabilities(), prediction.get_multipliers()):
                final_prediction += pred * multiplier
            final_predictions[term_id] = final_prediction

        self.predictions_by_term = final_predictions

    '''
    Extracts the abstract and full text from a file and predicts the terms
    '''
    async def predict_for_file(self, file):
        print("Predicting for file: ", file)
        abstract, full_text = await get_text_from_file(file)
        print("Abstract: ", abstract)
        print("Full text: ", full_text)

        data_input = {"abstract": abstract, "normal": full_text, "tf-idf": full_text}

        # Iterate through the input creators
        for input_creator in self.input_creators:
            self.log.info(f"Predicting with input creator: {input_creator}")
            predictions = self.predict_terms(input_creator, data_input[input_creator])
            self.generate_predictions(predictions)

        self.print_predictions()
