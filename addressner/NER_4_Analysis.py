from json import load as json_load
from pprint import pprint
from matplotlib.pyplot import subplots, tight_layout, show
from matplotlib.colors import ListedColormap
from numpy import mod
from pandas import DataFrame, set_option
set_option('display.max_columns', None)
set_option('display.precision', 3)


# Load and print scores
with open('../Data/NER/models_scores.json', 'r') as f:
    scores = json_load(f)

pprint(scores)


# Build dataframes to show the scores better and print them
n_batches = 5
tr_te = ['test', 'train']
model_names = ['en_' + str(b) for b in range(n_batches)] + ['es_' + str(b) for b in range(n_batches)]
gen_metric_names = ['acc', 'ents_p', 'ents_r', 'ents_f']
entities = ['N', 'S', 'M', 'PC', 'SP', 'C']
spe_metric_names = ['p', 'r', 'f']

gen_metrics = {(met, tt): [scores[tt][mn][met] for mn in model_names]
               for met in gen_metric_names for tt in tr_te}
spe_metrics = {(ent, met, tt): [scores[tt][mn]['ents_per_type'][ent][met] for mn in model_names]
               for ent in entities for met in spe_metric_names for tt in tr_te}

gen = DataFrame(gen_metrics, index=model_names)
spe = DataFrame(spe_metrics, index=model_names)

gen_means = DataFrame([gen.iloc[:n_batches].mean(), gen.iloc[n_batches:].mean()], index=['en', 'es'])
gen_stds = DataFrame([gen.iloc[:n_batches].std(), gen.iloc[n_batches:].std()], index=['en', 'es'])

spe_means = DataFrame([spe.iloc[:n_batches].mean(), spe.iloc[n_batches:].mean()], index=['en', 'es'])
spe_stds = DataFrame([spe.iloc[:n_batches].std(), spe.iloc[n_batches:].std()], index=['en', 'es'])

print('Average scores for each model:', gen, sep='\n', end='\n\n')
print('Scores per entity per model:', spe, sep='\n', end='\n\n')
print('Mean of the average scores for each model:', gen_means, sep='\n', end='\n\n')
print('Mean of the scores per entity per model:', spe_means, sep='\n', end='\n\n')
print('Standard deviation of the average scores for each model:', gen_stds, sep='\n', end='\n\n')
print('Standard deviation of the scores per entity per model:', spe_stds, sep='\n', end='\n\n')


# Graphics of the scores and their plotting configuration
spe_metric_names_complete = ['Precision', 'Recall', 'F1-score']
gen_metric_names_complete = ['Accuracy'] + spe_metric_names_complete
spe_cm = [ListedColormap(['pink', 'red']),
          ListedColormap(['lightblue', 'blue']),
          ListedColormap(['lightgreen', 'green'])]
gen_cm = [ListedColormap(['gold', 'darkorange'])] + spe_cm

# Average scores for each model
fig_gen, ax = subplots(2, 2, figsize=(12, 8))
axes = ax.ravel()
for i in range(4):
    gen[gen_metric_names[i]].plot(kind='bar', title=gen_metric_names_complete[i], ylim=[50, 100], rot=0,
                                  ax=axes[i], sharex=True, sharey=True, colormap=gen_cm[i], fontsize=12)

for axe in ax.flatten():
    axe.axvline(x=n_batches - 0.5, linewidth=0.75, color='k')
    axe.title.set_size(15)
    axe.tick_params(left=True, right=True)
tight_layout()
show()

# Scores per entity per model
fig_spe, ax = subplots(len(entities), len(spe_metric_names), figsize=(15, 20))
axes = ax.ravel()
ent_graph = [element for sublist in [[ent]*len(spe_metric_names) for ent in entities] for element in sublist]
for i in range(len(spe_metric_names) * len(entities)):
    spe[ent_graph[i]][spe_metric_names[mod(i, len(spe_metric_names))]].plot(kind='bar',
                            title=(spe_metric_names_complete + [''] * (len(spe_metric_names) * (len(entities) - 1)))[i],
                            ylabel=ent_graph[i] + '   ', ylim=[50, 100], rot=0, ax=axes[i], sharex=True, sharey=True,
                            colormap=spe_cm[mod(i, len(spe_metric_names))], fontsize=12)

for axe in ax.flatten():
    axe.axvline(x=n_batches - 0.5, linewidth=0.75, color='k')
    axe.title.set_size(16)
    axe.yaxis.label.set_rotation(0)
    axe.yaxis.label.set_size(25)
    axe.tick_params(left=True, right=True)
tight_layout()
show()


# Save figures
fig_gen.savefig('../Data/NER/models_scores_gen.png')
fig_spe.savefig('../Data/NER/models_scores_spe.png')
