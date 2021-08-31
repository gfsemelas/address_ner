from pickle import load as pickle_load
from spacy import load as spacy_load
from tqdm import tqdm
from addressner.sources.ner import predict, evaluate, accuracy
from numpy import mod
from json import dump as json_dump
from warnings import filterwarnings
filterwarnings('ignore', category=UserWarning)


# Load train and test addresses
n_batches = 5
trains = []
tests = []
for b in range(n_batches):
    with open('../Data/NER/train_test_pred/train_batch' + str(b) + '.txt', 'rb') as f:
        trains.append(pickle_load(f))
    with open('../Data/NER/train_test_pred/test_batch' + str(b) + '.txt', 'rb') as f:
        tests.append(pickle_load(f))

# Load NER models
model_names = ['en_' + str(b) for b in range(n_batches)] + ['es_' + str(b) for b in range(n_batches)]
ner_models = [spacy_load('../Data/NER/models/' + mn) for mn in tqdm(model_names)]

# Make predictions for the train and the test data
preds_train = [predict(ner_models[i], trains[mod(i, n_batches)], des='train_'+mn,
                       path='../Data/NER/train_test_pred/pred/', suffix='train_'+mn)
               for i, mn in enumerate(model_names)]
preds_test = [predict(ner_models[i], tests[mod(i, n_batches)], des='test_'+mn,
                      path='../Data/NER/train_test_pred/pred/', suffix='test_'+mn)
              for i, mn in enumerate(model_names)]

# Evaluate models
train_scores = {mn: evaluate(ner_models[i], trains[mod(i, n_batches)], des='train_' + mn)
                for i, mn in enumerate(model_names)}
test_scores = {mn: evaluate(ner_models[i], tests[mod(i, n_batches)], des='test_' + mn)
               for i, mn in enumerate(model_names)}

# Compute accuracy of the models
for i, mn in enumerate(model_names):
    train_scores[mn]['acc'] = accuracy(trains[mod(i, n_batches)], preds_train[mod(i, n_batches)])
    test_scores[mn]['acc'] = accuracy(tests[mod(i, n_batches)], preds_test[mod(i, n_batches)])

# Save scores
scores = {'train': train_scores, 'test': test_scores}
with open('../Data/NER/models_scores.json', 'w') as f:
    json_dump(scores, f)
