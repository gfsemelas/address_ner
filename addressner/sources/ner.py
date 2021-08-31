from random import sample
from pickle import dump as pickle_dump
from json import dump as json_dump
from spacy import blank
import spacy
from tqdm import tqdm
from numpy import mean
from spacy.scorer import Scorer
from spacy.gold import GoldParse


def train_test_split(data: list,
                     train_ratio: float = 0.7,
                     save: bool = True,
                     path: str = '',
                     prefix: str = '',
                     suffix: str = '',
                     file_format: (str, list) = ('txt', 'json')) -> tuple:
    """
    This function performs a train-test split.

    :param data: data
    :param train_ratio: ratio of data records to make up the training set
    :param save: whether to save the train and test sets or not
    :param path: where to save the train and test sets if "save=True"
    :param prefix: prefix to 'train' or 'test' words in the name of the files if "save=True"
    :param suffix: suffix to 'train' or 'test' words in the name of the files if "save=True"
    :param file_format: format of the saved files if "save=True"
    :return: train and test sets
    """
    data_random = sample(data, len(data))
    split = round(train_ratio * len(data))
    train = data_random[:split]
    test = data_random[split:]

    if save:
        file_format = file_format if isinstance(file_format, (list, tuple)) else [file_format]
        path = path if (path == '' or path[-1] == '/') else path + '/'
        suffix = '_' + str(suffix) if len(str(suffix)) > 0 else suffix
        prefix = str(prefix) + '_' if len(str(prefix)) > 0 else prefix
        name_train = path + prefix + 'train' + suffix
        name_test = path + prefix + 'test' + suffix

        if 'txt' in file_format:
            with open(name_train + '.txt', 'wb') as f:
                pickle_dump(train, f)
            with open(name_test + '.txt', 'wb') as f:
                pickle_dump(test, f)

        if 'json' in file_format:
            with open(name_train + '.json', 'w') as f:
                json_dump(train, f)
            with open(name_test + '.json', 'w') as f:
                json_dump(test, f)

    return train, test


def address_ner(train_data: list,
                entities: list = (),
                lang: str = 'en',
                optimizer=None,
                name: str = 'address_ner',
                progress: bool = True,
                save: bool = True,
                path: str = '') -> spacy.lang:
    """
    Function to train a NER model from scratch.

    :param train_data: training data
    :param entities: entities to identify. If no provide, the NER model automatically detects them
    :param lang: language in which base the NER model
    :param optimizer: optimizer. If no optimizer is provided, the NER model automatically chooses an appropriate one
    :param name: name of the NER model
    :param progress: whether to show progress with "tqdm" or not
    :param save: whether to save the NER model or not (if True it will be saved with name "name")
    :param path: path where to save the NER model if "save=True"
    :return: spaCy NER model
    """
    # New, empty model
    nlp = blank(lang)

    # Give a name to the list of vectors
    nlp.vocab.vectors.name = name

    # Add NER pipeline (the pipeline would just do NER)
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

    # Add new entity labels to entity recognizer
    for ent in entities:
        nlp.entity.add_label(ent)

    # Initializing optimizer. Custom optimizers: https://thinc.ai/docs/api-optimizers
    if optimizer is None:
        optimizer = nlp.begin_training()

    # Update the model with the training data
    if progress:
        train_data = tqdm(train_data, desc=name)
    for text, annotations in train_data:
        nlp.update([text], [annotations], sgd=optimizer)

    # Save model
    if save:
        path = path if (path == '' or path[-1] == '/') else path + '/'
        nlp.to_disk(path + name)

    return nlp


def predict(model: spacy.lang,
            data: list,
            progress: bool = True,
            des: str = '',
            save: bool = True,
            path: str = '',
            prefix: str = '',
            suffix: str = '',
            file_format: (str, list) = ('txt', 'json')) -> list:
    """
    This function makes a prediction for the data using a NER model.

    :param model: NER model
    :param data: input data for the model in order to make a prediction
    :param progress: whether to show progress with "tqdm" or not
    :param des: description for the "tqdm" Wrapper if "progress=True"
    :param save: whether to save the predictions or not
    :param path: where to save the predictions if "save=True"
    :param prefix: prefix to 'pred' word in the name of the files if "save=True"
    :param suffix: suffix to 'pred' word in the name of the files if "save=True"
    :param file_format: format of the saved files if "save=True"
    :return: prediction
    """
    if progress:
        data = tqdm(data, desc=des)

    pred = [(address[0], {'entities': [(entity.start_char, entity.end_char, entity.label_)
                                       for entity in model(address[0]).ents]})
            for address in data]

    if save:
        file_format = file_format if isinstance(file_format, (list, tuple)) else [file_format]
        path = path if (path == '' or path[-1] == '/') else path + '/'
        suffix = '_' + str(suffix) if len(str(suffix)) > 0 else suffix
        prefix = str(prefix) + '_' if len(str(prefix)) > 0 else prefix
        name = path + prefix + 'pred' + suffix

        if 'txt' in file_format:
            with open(name + '.txt', 'wb') as f:
                pickle_dump(pred, f)

        if 'json' in file_format:
            with open(name + '.json', 'w') as f:
                json_dump(pred, f)

    return pred


def accuracy(data: list,
             preds: list,
             percentage: bool = True) -> float:
    """
    Function to compute the accuracy of predictions compared to the real data.

    :param data: real data
    :param preds: predictions
    :param percentage: whether returning the accuracy over 100% or not
    :return: accuracy
    """
    acc = []
    for i in range(len(preds)):
        good = 0
        for ent in preds[i][1]['entities']:
            good += 1 if ent in data[i][1]['entities'] else 0
        try:
            good_ratio = good / len(preds[i][1]['entities'])
        except ZeroDivisionError:
            good_ratio = 0
        acc.append(good_ratio)
    factor = 100 if percentage else 1
    return mean(acc) * factor


def evaluate(ner_model: spacy.lang,
             data: list,
             progress: bool = True,
             des: str = '') -> dict:
    """
    Function to evaluate a NER model.

    :param ner_model: NER model
    :param data: data with which to evaluate the model
    :param progress: whether to show progress with "tqdm" or not
    :param des: description for the "tqdm" Wrapper if "progress=True"
    :return: dictionary with detailed performance scores
    """
    scorer = Scorer()
    if progress:
        data = tqdm(data, desc=des)
    for address, annot in data:
        doc_gold_text = ner_model.make_doc(address)
        gold = GoldParse(doc_gold_text, entities=annot['entities'])
        pred_value = ner_model(address)
        scorer.score(pred_value, gold)
    return {key: scorer.scores.get(key) for key in ['ents_p', 'ents_r', 'ents_f', 'ents_per_type']}
