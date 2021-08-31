from pandas import read_csv
from addressner.sources.cleaning import cleaning
from pickle import dump


# Load the data. The csv separator is "μ" (\u03bc)
header = ['CLIENT_ID', 'ADDRESS', 'POSTALCODE', 'CITY', 'STATE', 'COUNTRY']
df = read_csv('../Data/20210311_GBOGL_Addresses.csv', sep='\u03bc', header=None, names=header, engine='python')

# Drop 'NaN's in 'ADDRESS' column
df.dropna(subset=['ADDRESS'], inplace=True)
df.reset_index(drop=True, inplace=True)

# Clean 'ADDRESS' field
df['ADDRESS_clean'] = [cleaning(row) for row in df['ADDRESS'].to_list()]

# Create new column 'all_clean' joining all information of each row
df['all_clean'] = df['ADDRESS_clean'].str.cat(df[['POSTALCODE', 'CITY', 'STATE', 'COUNTRY']], sep=' ', na_rep='')

# Save clean addresses into .txt file
with open('../Data/AzureMaps results/addresses.txt', 'wb') as f:
    dump(df['all_clean'].to_list(), f)
