from re import sub


def sub_accents(sentence: str,
                lower: bool = True) -> str:
    """
    This function substitutes all accented letters with the corresponding letter without the accent.

    :param sentence: string to remove accents in
    :param lower: whether converting sentence to lowercase or not
    :return: sentence with accents removed
    """
    if lower:
        sentence = sentence.lower()

    # List of possible accents per letter and their respective replacement
    a = r'á|à|â|ä|ã'
    e = r'é|è|ê|ë'
    i = r'í|ì|î|ï'
    o = r'ó|ò|ô|ö|õ'
    u = r'ú|ù|û|ü'
    c = r'ç'
    n = r'ñ'
    y = r'ý|ÿ'
    regexps = [a, e, i, o, u, c, n, y]
    letters = ['a', 'e', 'i', 'o', 'u', 'c', 'n', 'y']

    # Convert accented letters into normal letters
    for i in range(len(regexps)):
        sentence = sub(regexps[i], letters[i], sentence)
        sentence = sub(regexps[i].upper(), letters[i].upper(), sentence)

    return sentence


def clean_additional_info(sentence: str,
                          info_to_substitute: (str, list, None) = None,
                          info_replacement: str = ' ',
                          lower: bool = True) -> str:
    """
    This function substitutes all regular expressions in "info_to_substitute" with "replacement".

    :param sentence: string to remove information in
    :param info_to_substitute: regular expression or list containing regular expressions with the information to remove
    :param info_replacement: replacement of all matches of the regular expressions of "info_to_substitute" in "sentence"
    :param lower: whether converting sentence to lowercase or not
    :return: sentence with information substituted
    """
    if lower:
        sentence = sentence.lower()

    # If no "info_to_remove" is given, default "info_to_substitute" aims to clean up address additional information...
    if info_to_substitute is None:
        # Patterns and stopwords to remove (all lowercase)
        pattern = r'\d{1,3}\W{0,2}[a-z]{0,2}'
        stopwords_ap = ['floor', 'derecha', 'izquierda', 'dcha', 'izda', 'izqda', 'departamento', 'apto', 'dpto',
                        'depto', 'apartment', 'department', 'apt', 'dpt', 'door', 'first', 'second', 'third', 'fourth',
                        'fifth', 'sixth', 'seventh', 'eighth', 'nineth', 'tenth']
        stopwords_bp = ['piso', 'derecha', 'izquierda', 'dcha', 'izda', 'izqda', 'apartamento', 'departamento', 'apto',
                        'dpto', 'depto', 'dp', 'apartment', 'department', 'apt', 'dpt', 'puerta', 'pta', 'door', 'bajo',
                        'entresuelo', 'sotano', 'bloque', 'portal', 'salon', 'primero', 'segundo', 'tercero', 'cuarto',
                        'quinto', 'sexto', 'septimo', 'octavo', 'noveno', 'decimo', 'suite']

        # Join "pattern" and stopwords in corresponding order
        stopwords_pattern = [r'{}'.format(sw_bp) + r'\W{0,1}' + pattern for sw_bp in stopwords_bp]
        pattern_stopwords = [pattern + r'\s{0,1}' + r'{}'.format(sw_ap) for sw_ap in stopwords_ap]

        # Regular expressions to substitute
        p1 = r'|'.join(stopwords_pattern + pattern_stopwords)
        p2 = r'|'.join(stopwords_pattern + pattern_stopwords)
        p3 = r'|'.join(list(set(stopwords_ap + stopwords_bp)))
        p4 = r'\s\d{1,2}\W{0,2}[a-z]{1,2}$'

        # Default "info_to_substitute"
        info_to_substitute = [p1, p2, p3, p4]

    # ... else convert "info_to_remove"
    else:
        info_to_substitute = [info_to_substitute]

    # Substitute info_to_remove with replacement
    for element in info_to_substitute:
        sentence = sub(element, info_replacement, sentence)

    # Remove additional blank spaces among words
    return ' '.join(sentence.split())


def clean_symbols(sentence: str,
                  symbol_replacement: str = ' ',
                  lower: bool = True) -> str:
    """
    This function substitutes all non alphanumeric characters with "replacement".

    :param sentence: string to remove symbols in
    :param symbol_replacement: replacement of all symbols in "sentence"
    :param lower: whether converting sentence to lowercase or not
    :return: sentence with all symbols substituted
    """
    if lower:
        sentence = sentence.lower()

    sentence = sub(r'[^a-zA-Z0-9\s]', symbol_replacement, sentence)

    # Remove additional blank spaces among words
    return ' '.join(sentence.split())


def cleaning(sentence: str,
             accents: bool = True,
             additional_info: bool = True,
             symbols: bool = True,
             **kwargs) -> str:
    """
    Function that performs full cleaning according to functions
    "sub_accents", "clean_additional_info" and "clean_accents".

    :param sentence: string to clean
    :param accents: whether applying "sub_accents" or not
    :param additional_info: whether applying "clean_additional_info" or not
    :param symbols: whether applying "clean_accents" or not
    :param kwargs: arguments of functions "sub_accents", "clean_additional_info" and "clean_accents".
    :return: sentence clean
    """
    if accents:
        sentence = sub_accents(sentence, **{key: value for key, value in kwargs.items() if
                                            key in sub_accents.__code__.co_varnames})
    if additional_info:
        sentence = clean_additional_info(sentence, **{key: value for key, value in kwargs.items() if
                                                      key in clean_additional_info.__code__.co_varnames})
    if symbols:
        sentence = clean_symbols(sentence, **{key: value for key, value in kwargs.items() if
                                              key in clean_symbols.__code__.co_varnames})

    return sentence
