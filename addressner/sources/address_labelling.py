def generate_ngrams(s, n):
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split()]
    # Use the zip function to generate n-grams
    ngrams = zip(*[tokens[i:] for i in range(n)])
    # Concatentate the tokens into ngrams and return
    return [' '.join(ngram) for ngram in ngrams]


def levenshtein(s, t, ratio_calc=True):
    '''
    Calculates Levenshtein distance between two strings.
    If ratio_calc=True, the function computes the Levenshtein distance ratio of similarity between two strings.
    For all i and j, distance[i,j] will contain the Levenshtein distance between the first i characters of s
    and the first j characters of t. (https://www.datacamp.com/community/tutorials/fuzzy-string-python)
    '''
    from numpy import zeros

    # Initialize matrix of zeros
    rows = len(s) + 1
    cols = len(t) + 1
    distance = zeros((rows, cols), dtype=int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0  # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package,
                # if we choose to calculate the ratio the cost of a substitution is 2.
                # If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row - 1][col] + 1,  # Cost of deletions
                                     distance[row][col - 1] + 1,  # Cost of insertions
                                     distance[row - 1][col - 1] + cost)  # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        try:
            Ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        except UnboundLocalError:
            Ratio = 0.0
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes
        # the cost of deletions, insertions and/or substitutions.
        # This is the minimum number of edits needed to convert string s to string t
        return 'The strings are {} edits away'.format(distance[row][col])


def identify_features(sentence, tags, tol=0.6):
    # Find all possible n-grams in sentence
    ngrams = []
    for i in range(len(sentence)):
        ngrams += generate_ngrams(sentence, i)

    # Calculate levenshtein distance of 'tag' and every gram
    if isinstance(tags, str):
        tags = [tags]
    lev = []
    for tag in tags:
        l = []
        for gram in ngrams:
            l.append(levenshtein(gram, tag))
        if max(l) > tol:
            r = ngrams[l.index(max(l))]
        else:
            r = 'NONE'
        lev.append(r)

    #     # Everything in "sentence" not in "lev" is AI (Additional Information)
    #     smod = sentence
    #     for element in reversed(lev):
    #         smod = smod.replace(element, '')
    #     lev.append(smod)

    return lev


def overlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def address_labelling(entities, sentence, tags, tol=0.6):
    from re import finditer

    matches = identify_features(sentence, tags, tol)
    entity_info = []
    for ei, element in enumerate(matches):
        for emi, element_mod in enumerate([' ' + element + ' ', ' ' + element, element + ' ', element]):
            break_loop = False
            start_end_iters = [(m.start(0), m.end(0)) for m in finditer(element_mod, sentence)]
            for (start_raw, end_raw) in start_end_iters:
                start = start_raw + 1 if emi in [0, 1] else start_raw
                end = end_raw - 1 if emi in [0, 2] else end_raw

                overs = []
                for i in range(len(entity_info)):
                    overs.append(overlap((start, end), entity_info[i][:2]))

                unique = element == sentence
                scorr = 1 if start == 0 else 0
                ecorr = -1 if end == len(sentence) else 0
                first = element.split()[0] == sentence.split()[0] and sentence[end + ecorr] == ' '
                last = element.split()[-1] == sentence.split()[-1] and sentence[start + scorr - 1] == ' '
                between = sentence[start + scorr - 1] == ' ' and sentence[end + ecorr] == ' '

                if not any(overs) and (unique or first or last or between):
                    entity_info.append((start, end, entities[ei]))
                    break_loop = True
                    break
            if break_loop:
                break

    return (sentence, {'entities': list(dict.fromkeys(entity_info))})
