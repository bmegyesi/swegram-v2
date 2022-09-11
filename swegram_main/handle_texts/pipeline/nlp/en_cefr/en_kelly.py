# to extract dict for kelly-list of english

import pyexcel_xlsx as pe
from collections import defaultdict
import json

"""
source: http://corpus.leeds.ac.uk/serge/kelly/
change on original file for frequency list in english
dependenceNoun --> dependence Noun
probable       --> probable   Adjective
presidential   --> presidential Adjective
preventive     --> preventive   Adjetive
"""


"""
contractions
data        Noun    A2 B1
third       Number  A1 B1
prior       ADJ     B1 B2
button      Noun    A2 B2
media       Noun    A1 C2
pencil      Noun    A2 C2
psychology  Noun    C1 C2
philosophy  Noun    B1 C2

"""


f = pe.get_data('en_m3.xlsx')
word_list = f['eng_with_all']

pos_convert = {
            "Adjective":"ADJ",
            "Adverb":"ADV",
            "Conjunction":"CCONJ",
            "Determiner":"DET",
            "Exclamation":"INTJ",
            "Model verb":"AUX",
            "Noun":"NOUN",
            "noun":"NOUN",
            "Number":"NUM",
            "Preposition":"ADP",
            "Pronoun":"PRON",
            "Verb":"VERB"
            }

cefr = {
    'A1':"1",
    'A2':"2",
    'B1':"3",
    'B2':"4",
    'C1':"5",
    'C2':"6"
}

"""
pos not in included in kelly list for english:
Abbreviation:   'etc', 'pm', 'et', 'ie', 'am', 'MA', 'km', 'approx', 'vs'
                'approx':"ADV",
                'km': "NOUN",
                'vs': "ADP",
                'pm': "NOUN",
                'etc': "X",
                'et': "NOUN", (Eastern Time)
                'to': "PART",
                'MA': "PROPN",
                "ie": X,
                "e.g.": X              
Miscellaneous: to e.g.
Modal Verb: have to
"""



res_dict = {}
#print([e[1] for e in word_list if e[2]=='Abbreviation'])

for entry in word_list:
    _, word, pos, c, _ = entry
    c = c[1:-1]
    if word[0] == '#':
        continue
    if pos in pos_convert:
        key = '|'.join([word.strip(), pos_convert[pos]])
        if key in res_dict:
            print('error', key, res_dict[key], cefr[c])
        else:
            res_dict[key] = cefr[c]


#with open('en_kelly_cefr', 'w') as outfile:
#    json.dump(res_dict, outfile)



        
    
    