import glob
import logging
import spacy
from app.utils.input_creators import get_prediction_multiplier
from app.models.Prediction import Prediction

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHILDREN_THRESHOLD = 0.4
PREDICTION_THRESHOLD = 0.5

class TermPrediction:
    def __init__(self, input_creator):
        self.input_creator = input_creator
        self.nlp = None
        self.log = logging.getLogger('predictor_logger')

    """
    Retrieve and load the saved spaCy model for a specific term.
    The model should have been previously saved to disk.
    """
    def get_model_for_term(self, term_id):
        model_path = f"./models/{self.input_creator}/{term_id}"
        
        try:
            # Check if the model path exists, then load the model
            if not glob.glob(model_path):
                self.log.error(f"Model for term {term_id} not found at path: {model_path}")
                return False
            else:
                # Load the saved spaCy model from disk
                print(f"Loading spaCy model from: {model_path}", flush=True)
                self.nlp = spacy.load(model_path)  # Load the specific model for this term
                return True
        except Exception as e:
            self.log.error(f"Error loading model for term {term_id}: {e}")
            return False

    """
    Perform prediction using a specific spaCy model loaded for the term.
    """
    def predict_text_with_model(self, text, term_id):
        predicted_terms = []
        predicted_children_ids = []
        predictions_log = []

        doc = self.nlp(text)  # Process the text with the loaded spaCy model
        for cat, score in doc.cats.items():
            predictions_log.append(f"{cat}: {score:.4f}")
            if score > PREDICTION_THRESHOLD:
                prediction_obj = Prediction(cat, doc.cats[cat], get_prediction_multiplier(self.input_creator), self.input_creator, term_id)

                predicted_terms.append(prediction_obj)
            if score > CHILDREN_THRESHOLD:
                predicted_children_ids.append(cat)

        self.log.info(f"Predictions: {', '.join(predictions_log)}")

        return predicted_terms, predicted_children_ids

        # Score supera PREDICTION -> guardar como un predicted term
        #            prediction_obj = Prediction(term, doc.cats[term], get_prediction_multiplier(self.input_creator))
        #             predicted_terms.append(prediction_obj)
        # Score supera CHILDREN PREDICTION -> guardar como un id y apendearlo a un predicted_children_terms (son ids)

    '''
    Recursive function to predict the terms (Initially predicted terms are empty)
    '''
    def predict_text(self, text, term_id, predicted_terms):
        self.log.info(f"Started predicting for term: {term_id}")
        print(f"Started predicting for term: {term_id}", flush=True)

        # Load the saved spaCy model for the term
        model_has_loaded = self.get_model_for_term(term_id)
        if model_has_loaded is not True:
            print(f"Model for term {term_id} not found", flush=True)
            return predicted_terms  # Skip if the model for the term is not found

        # Use the loaded model to predict the terms
        selected_terms, selected_children_ids = self.predict_text_with_model(text, term_id)

        if selected_terms:
            predicted_terms.extend(selected_terms)

        # If the prediction returns children, recursively predict for them
        if len(selected_children_ids):
            for selected_children_id in selected_children_ids:
                self.predict_text(text, selected_children_id, predicted_terms)

        return predicted_terms
