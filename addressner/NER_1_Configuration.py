from pandas import read_csv, DataFrame
from zipfile import ZipFile
from addressner.sources.cleaning import cleaning
from tqdm import tqdm
from json import load as json_load
from json import dump as json_dump
from pickle import dump as pickle_dump
from addressner.sources.address_labelling import address_labelling


# Load the data. The csv separator is "μ" (\u03bc)
header = ['CLIENT_ID', 'ADDRESS', 'POSTALCODE', 'CITY', 'STATE', 'COUNTRY']
n_rows = 88000
zf = ZipFile('../Data/20210311_GBOGL_Addresses.zip')
df = read_csv(zf.open('20210311_GBOGL_Addresses.csv'),
              sep='\u03bc', header=None, names=header, engine='python', nrows=n_rows*1.25)
zf.close()

# Drop 'NaN's in 'ADDRESS' column and preserve only the records that were labelled with Azure Maps
df.dropna(subset=['ADDRESS'], inplace=True)
df.reset_index(drop=True, inplace=True)
df = df[:n_rows]

# Create new column 'all' joining all information of each row: the full address
df['all'] = df['ADDRESS'].str.cat(df[df.columns[2:]], sep=' ', na_rep='')

# Clean the addresses
df['all_clean'] = [cleaning(row, additional_info=False) for row in tqdm(df['all'].to_list(), desc='Cleaning addresses')]

# Read the results of the queries to Azure Maps
dt = 2000
tmax = n_rows
results = []
for t in tqdm(range(0, tmax, dt), desc='Reading Azure Maps results'):
    with open(f'../Data/AzureMaps results/AMr_{t}-{t+dt}.json', 'r', encoding='utf-8') as f:
        results += json_load(f)

# Features of the results that are kept for future NER and their abbreviations
features = ['streetNumber', 'streetName', 'municipality', 'countrySubdivision',
            'countrySubdivisionName', 'postalCode', 'extendedPostalCode', 'country']
entities = ['N', 'S', 'M', 'SP', 'SP', 'PC', 'PC', 'C']

# Get the features from the Azure Maps results
f = []
exception = '-'
for res in results:
    r = []
    for feat in features:
        try:
            r.append(res['results'][0]['address'][feat].lower())
        except:
            r.append(exception)
    f.append(r)

# Assign the features to the corresponding address in a dataframe
data = df['all_clean'].to_frame().merge(DataFrame(f, columns=features), left_index=True, right_index=True)

# Label addresses in a format that spaCy will understand
labelled_data = [address_labelling(entities, data['all_clean'].iloc[i], data[features].iloc[i])
                 for i in tqdm(range(data.shape[0]), desc='Building NER training')]

# Save addresses labelled
with open('../Data/NER/ner_train.txt', 'wb') as ftxt:
    pickle_dump(labelled_data, ftxt)

with open('../Data/NER/ner_train.json', 'w') as fjson:
    json_dump(labelled_data, fjson)
