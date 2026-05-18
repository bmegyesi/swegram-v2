# Spelling Normalization from Yuchan HONG, September 2018
# Modified by Eva Pettersson, eva.pettersson@lingfil.uu.se

from __future__ import with_statement
from __future__ import absolute_import
import sys
import re
import Levenshtein
import difflib
import jellyfish
import glob
import os
from codecs import open

# Paths to input and output files are given as arguments


def enggram_spellcheck(inputFileName, outputFileName):

    current_path = os.path.dirname(os.path.abspath(__file__))

    # Paths to dictionaries are given below:
    dic = current_path + '/WordNetDictionary'
    corpus = current_path + '/bnc.mono.en.freqs'
    wfiles = os.listdir(dic)

    wdict = []

    for w in wfiles:
        with open(os.path.join(dic, w), 'r', encoding='utf8') as f:
            if u'exc' in w:
                for line in f:
                    if not re.search(u'_', line):
                        line = line.lower()
                        line = line.rstrip()
                        line = line.split(u' ')
                        for i in line:
                            wdict.append(i)
            if u'data' in w:
                if u'verb' in w:
                    for line in f:
                        if not re.search(u'_', line):
                            line = line.lower()
                            line = line.split(u' ')
                            i = line[4]
                            wdict.append(i)
    #                    wdict.append(i+'s')
    #                    if i[-1] == 'e':
    #                        wdict.append(i[0:-1]+'ing')
    #                        wdict.append(i[0:-1]+'ed')
    #                    else:
    #                        wdict.append(i+'ing')
    #                        wdict.append(i+'ed')
                if u'noun' in w:
                    for line in f:
                        if not re.search(u'_', line):
                            line = line.lower()
                            line = line.split(u' ')
                            i = line[4]
                            wdict.append(i)
    #                    wdict.append(i+'s')
                else:
                    for line in f:
                        if not re.search(u'_', line):
                            line = line.lower()
                            line = line.split(u' ')
                            i = line[4]
                            wdict.append(i)

    wdictset = set(wdict)
    wdicts = list(wdictset)

    wdictfreq = {}
    for word in wdicts:
        wdictfreq[word] = 0

    #wdictfreq[''] = 0
    #wdictfreq['<'] = 0
    #wdictfreq['>'] = 0
    #wdictfreq["''"] = 0
    #wdictfreq["``"] = 0
    #wdictfreq['/title'] = 0

    with open(corpus, 'r', encoding='utf8') as g:
        for line in g:
            lineMatch = re.search(r'^\s*(\d+)\s+(.+?)\s*$', line)
            freq = lineMatch.group(1)
            token = lineMatch.group(2)
            wdictfreq[token] = freq

    out = {}
    outcandi = {}
    levencandi = []
    compound = []
    first = []

    # search the input file for unseen spellings
    with open(inputFileName, 'r', encoding='utf8') as f:
        for i in f:
            if not re.match(r'^\#', i):
                i = i.rstrip()
                i = re.sub(r'^\d+\t([^\t]+)\t.+$', r'\1', i)

                if i not in wdictfreq.keys():
                    if not i.lower() in wdictfreq.keys():
                        if not re.findall(r'-', i):  # why exclude compounds with hyphen?
                            if not re.findall(r'\d+', i):
                                levencandi.append(i)
        f.close()
        levencandi = [word for word in levencandi if word.islower()]

    # print u'OOV words: ',len(levencandi),u'\n',levencandi

    # Gestalt approach
    for l in levencandi:
        out[l] = difflib.get_close_matches(l, wdictfreq.keys(), 6)
    #    print(out[l])

    # phonetic similarity using the Metaphone algorithm
    for k in out.keys():
        for v in out[k]:
            if k not in outcandi.keys():
                if jellyfish.metaphone(k) == jellyfish.metaphone(v):
                    outcandi[k] = {v: 0}
                    # same phonetic code, e.g.: "oppurtunity - opportunity"
                else:
                    outcandi[k] = {v: 1}
                    # different phonetic code, e.g.: "glosseries - glossiest"
            else:
                if jellyfish.metaphone(k) == jellyfish.metaphone(v):
                    outcandi[k].update({v: 0})
                else:
                    outcandi[k].update({v: 1})

    # string similarity using the Damerau Levenshtein distance algorithm
    for k in outcandi.keys():
        samedist = []
        if len(outcandi[k]) > 1:
            for v in outcandi[k]:
                outcandi[k].update(
                    {v: outcandi[k][v]+jellyfish.damerau_levenshtein_distance(k, v)})

        samedist = [v for v, e in outcandi[k].items() if e == 1]

    # frequency counts to distinguish between equally similar candidates
        if len(samedist) > 1:
            comp = {}
            for h in samedist:
                #comp[h] = wdictfreq[h]
                comp[h] = str(wdictfreq[h])  # modified by rex
            outcandi[k] = max(comp, key=comp.get)

        else:
            outcandi[k] = min(outcandi[k], key=outcandi[k].get)

    # compound analysis for candidates with an edit distance equal to or higher than 3
        if jellyfish.damerau_levenshtein_distance(k, outcandi[k]) >= 3:
            compound.append(k)

    # print u'compounds: ',u'\n',compound
    for c in compound:
        if re.findall(r'-', c):
            sub = u''
            splitter = c.split(u'-')
        if re.findall(r'/', c):
            sub = u''
            splitter = c.split(u'/')
            for s in splitter:
                submatch = difflib.get_close_matches(s, wdictfreq.keys(), 1)[0]
                sub = sub + submatch + u'-'
            outcandi[c] = sub[0:-1]
    #    else:
    #        splitter = c.split(outcandi[c])
    #        if splitter[0] != '':
    #            splitter = difflib.get_close_matches(splitter[0],wdictfreq.keys(),1)[0]
    #        else:
    #            splitter = difflib.get_close_matches(splitter[1],wdictfreq.keys(),1)[0]
    #
    #        if outcandi[c] == splitter:
    #            outcandi[c] = outcandi[c]
    #        else:
    #            if c[0:3] == outcandi[c][0:3]:
    #                outcandi[c] = outcandi[c] + '-' + splitter
    #            else:
    #                outcandi[c] = splitter + '-' + outcandi[c]
    # print u'normalization results: ',u'\n',outcandi

    # change the filenames to the unnormalized file and the output normalized file
    with open(inputFileName, 'r', encoding='utf8') as f:
        with open(outputFileName, 'w', encoding='utf8')as p:
            for line in f:
                line = line.rstrip()
                if re.match(r'^\#', line):
                    p.write(line)
                    p.write(u'\n')
                else:
                    head = re.sub(r'^(\d+\t[^\t]+\t)\_.+$', r'\1', line)
                    tail = re.sub(r'^\d+\t[^\t]+\t\_(.+)$', r'\1', line)
                    token = re.sub(r'^\d+\t([^\t]+)\t.+$', r'\1', line)
                    if token not in outcandi.keys():
                        p.write(head + token + tail)
                        p.write(u'\n')
                    else:
                        p.write(head + outcandi[token] + tail)
                        p.write(u'\n')
        f.close()
        p.close()
