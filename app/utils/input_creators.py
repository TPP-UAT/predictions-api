NORMAL_TRAIN = 0.3
TFIDF_TRAIN = 0.3
ABSTRACT_TRAIN = 0.4
SUMMARIZE_TRAIN_WEIGHT = 0.4


def get_prediction_multiplier(input_creator):
    if input_creator == 'normal':
        return NORMAL_TRAIN
    elif input_creator == 'tf-idf':
        return TFIDF_TRAIN
    elif input_creator == 'abstract':
        return ABSTRACT_TRAIN
    elif input_creator == 'summarize':
        return SUMMARIZE_TRAIN_WEIGHT
    else:
        return 0
