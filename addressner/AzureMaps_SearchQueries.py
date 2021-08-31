from zipfile import ZipFile
from pickle import load as pickle_load
from time import time, strftime
from addressner.sources.fetching import fetch_all
from asyncio import get_event_loop
from addressner.sources.elapsed_time import elapsed_time
from json import dump as json_dump


# Load addresses
with ZipFile('../Data/AzureMaps results/addresses.zip', 'r') as zip_read:
    zip_read.extractall()
with open('../Data/AzureMaps results/addresses.txt', 'rb') as f:
    addresses = pickle_load(f)

# Key and query for Azure Maps requests
subscriptionKey = 'INSERT_YOUR_KEY_HERE'
query_template = 'https://atlas.microsoft.com/search/address/json?&subscription-key='\
                 + subscriptionKey + '&api-version=1.0&language=en-US&query={}'

# Queries for addresses
queries = [query_template.format(a) for a in addresses]
# Modify these values in order to fetch more or less queries at a time
start = 0
end = 2000


print(f'Getting results. Started at {strftime("%d/%m/%Y-%H:%M:%S")} ...', end=' ')
t0 = time()

if __name__ == '__main__':
    loop = get_event_loop()
    results = loop.run_until_complete(fetch_all(2000, 5, queries[start:end], loop))

print(f'({elapsed_time(time() - t0)})')
print('Done!')


# Save results
with open('../Data/AzureMaps results/AMr_{}-{}.json'.format(start, end), 'w', encoding='utf-8') as f:
    json_dump(results, f)
