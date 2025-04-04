ABSTRACT_TRAIN = 0.35
SUMMARIZE_FULL_TEXT_TRAIN_WEIGHT = 0.25
SUMMARIZE_SUMMARIZE_TRAIN_WEIGHT = 0.4


def get_prediction_multiplier(input_creator):
    if input_creator == 'abstract':
        return ABSTRACT_TRAIN
    elif input_creator == 'summarize-full_text':
        return SUMMARIZE_FULL_TEXT_TRAIN_WEIGHT
    elif input_creator == 'summarize-summarize':
        return SUMMARIZE_SUMMARIZE_TRAIN_WEIGHT
    else:
        return 0
