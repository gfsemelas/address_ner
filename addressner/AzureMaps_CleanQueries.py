from pandas import read_csv
from zipfile import ZipFile
from addressner.sources.cleaning import cleaning
from pickle import dump as pickle_dump


# Load the data. The csv separator is "μ" (\u03bc)
header = ['CLIENT_ID', 'ADDRESS', 'POSTALCODE', 'CITY', 'STATE', 'COUNTRY']
zf_read = ZipFile('../Data/20210311_GBOGL_Addresses.zip')
df = read_csv(zf_read.open('20210311_GBOGL_Addresses.csv'),
              sep='\u03bc', header=None, names=header, engine='python')
zf_read.close()

# Drop 'NaN's in 'ADDRESS' column
df.dropna(subset=['ADDRESS'], inplace=True)
df.reset_index(drop=True, inplace=True)

# Clean 'ADDRESS' field
df['ADDRESS_clean'] = [cleaning(row) for row in df['ADDRESS'].to_list()]

# Create new column 'all_clean' joining all information of each row
df['all_clean'] = df['ADDRESS_clean'].str.cat(df[['POSTALCODE', 'CITY', 'STATE', 'COUNTRY']], sep=' ', na_rep='')

# Save clean addresses into .txt file, and compress it
with open('../Data/AzureMaps results/addresses.txt', 'wb') as f:
    pickle_dump(df['all_clean'].to_list(), f)

zf_write = ZipFile('addresses.zip', 'w')
zf_write.write('addresses.csv')
zf_write.close()
