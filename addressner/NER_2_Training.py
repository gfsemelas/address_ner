from pickle import load as pickle_load
from addressner.sources.ner import train_test_split, address_ner
from warnings import filterwarnings
filterwarnings('ignore', category=UserWarning)


# Load data
with open('../Data/NER/labelled_data.txt', 'rb') as f:
    data = pickle_load(f)

# Entities for NER
entities = ['N', 'S', 'M', 'SP', 'PC', 'C']
# LEGEND
#     N = streetNumber
#     S = streetName
#     M = municipality
#    SP = countrySubdivision / countrySubdivisionName'
#    PC = postalCode / extendedPostalCode
#     C = country

# Train-test split
n_batches = 5
tt = [train_test_split(data, path='../Data/NER/train_test_pred/', suffix=f'batch{batch}') for batch in range(n_batches)]
train_batches, test_batches = list(zip(*tt))

# Train NER models, one per batch and language (english, spanish)
nlp_en = [address_ner(train_batches[b], entities=entities, lang='en', name='en_'+str(b), path='../Data/NER/models/')
          for b in range(n_batches)]
nlp_es = [address_ner(train_batches[b], entities=entities, lang='es', name='es_'+str(b), path='../Data/NER/models/')
          for b in range(n_batches)]
