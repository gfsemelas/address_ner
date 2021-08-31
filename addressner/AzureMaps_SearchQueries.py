from pickle import load
from time import time, strftime
from addressner.sources.fetching import fetch_all
from asyncio import get_event_loop
from addressner.sources.elapsed_time import elapsed_time


# Load addresses
with open('../Data/AzureMaps results/addresses.txt', 'rb') as f:
    addresses = load(f)

# Key and query for Azure Maps requests
subscriptionKey = 'INSERT_YOUR_KEY_HERE'
query_template = 'https://atlas.microsoft.com/search/address/json?&subscription-key='\
                 + subscriptionKey + '&api-version=1.0&language=en-US&query={}'

# Queries for addresses
queries = [query_template.format(a) for a in addresses]



print(f'Getting results. Started at {strftime("%d/%m/%Y-%H:%M:%S")} ...', end=' ')
t0 = time()

if __name__ == '__main__':
    loop = get_event_loop()
    results = loop.run_until_complete(fetch_all(2000, 5, queries, loop))

print(f'({elapsed_time(time() - t0)})')
print('Done!')
