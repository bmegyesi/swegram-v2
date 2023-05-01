#!/usr/bin/env/ python3
#encoding: utf-8

# This script is to collect syntactic features
# The list of syntactic features:

"""
dep_length_5+
dep_length_max
dep_length
dep_left
def_right
mod
pre
post
sub
relative
prep
"""


from .statistics import mean, median
from collections import OrderedDict, Counter
from .helpers import eval_str
from copy import deepcopy
import re


def is_a_ud_tree(sentence, upload_annotated=False):
    if upload_annotated:
        heads = [int(token.head) for token in sentence]  #This is used to check the sentence that has been annotated before
    else:
        heads = [int(token.head) for token in sentence.tokens]
    if not heads:
        if upload_annotated:
            return 'Heads not exist in sentence'
        return False
    children = list(range(1,len(heads)+1))
    if 0 not in heads:
        if upload_annotated:
            return "Root is missing"
        print("Root is missing in sentence %s!" % (sentence.text_id))
        return False
    if Counter(heads)[0] > 1:
        if upload_annotated:
            return 'More than one root in sentence'
        print("More than one root in sentence %s!" % (sentence.text_id))
        return False
    if len(children) > len(set(children)):
        if upload_annotated:
            return "Same indeces for two nodes"
        print("Same indeces for two nodes in sentence %s." % (sentence.text_id))
        return False
    
    for i in children:
        head = [heads[i - 1]]
        while 0 not in head:
            if heads[head[-1] - 1] in head:
                if upload_annotated:
                    return 'Cycle Error'
                print("Cycle Error in sentence %s." % (sentence.text_id))
                # print("It is Not a standard ud tree.")
                return False
            head.append(heads[head[-1] - 1])
        head = []
    return True

def get_path(n, heads): #n is an index in the sentence to identify the word
    path = [n]
    while n:
        path.append(heads[n])
        n = heads[n]
    return path

def dep_heads_helper(sentence):
    heads = [int(token.head) for token in sentence.tokens]
    heads.insert(0,None)
    return heads

def dep_paths(sentence):
    heads = dep_heads_helper(sentence)
    tokens = [token.norm for token in sentence.tokens]
    tokens.insert(0, "ROOT")
    dep_paths_list = []
    for i in range(1,len(heads)):
        dep_paths_list.append(get_path(i,heads))
    for path in dep_paths_list:
        for i in range(len(path)):
            path[i] = tokens[path[i]]
    return dep_paths_list

def arc5plus(sentence):
    dep_p = dep_paths(sentence)
    if not dep_p:
        return 0
    longarcs = []
    arc5 = 6  #6 nodes, 5 arcs
    for path in dep_p:
        while arc5 < len(path)+1:
            for i in range(len(path)+1-arc5):
                longarc = path[i:i+arc5]
                if longarc not in longarcs:
                    longarcs.append(longarc)
            arc5 += 1
        arc5 = 6
    return len(longarcs)


def dep_length_per_sentence(sentence):
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0
    dep_lengths = []
    for i in range(1,len(heads)):
        dep_lengths.append(get_path(i, heads))
    dep_length_nos = [len(path)-1 for path in dep_lengths] #nos: number of strings

    return round(sum(dep_length_nos)/float(len(dep_length_nos)),2)

def avg_dep_length(text):
    dep = 0
    for sentence in text.sentences:
        dep += dep_length_per_sentence(sentence)
    if not text.sentences:
        return 0.0
    return round(dep/float(len(text.sentences)), 2)

def median_dep_length(text):
    med = []
    for sentence in text.sentences:
        heads = dep_heads_helper(sentence)
        if not heads:
            return []
        for i in range(1, len(heads)):
            med.append(len((get_path(i, heads))))
    return med

def dep_dir_count(sentence, dir, ratio=False): #sentence and direction
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0, 0.0
    dir_arc = 0
    if dir == "left":
        for i in range(1, len(heads)):
            if heads[i] < i:
                dir_arc += 1
    else:
        for i in range(1, len(heads)):
            if heads[i] > i:
                dir_arc += 1
    if ratio:
        return round(dir_arc/float(len(heads)-1), 2)
    return dir_arc, len(heads)-1

def mod_incsc(sentence, pre_mod=False, post_mod=False):
    """A nominal head does not take any core arguments but may be associated with different types of modifiers:
    An nmod is a nominal phrase modifying the head of another nominal phrase, with or without a special case marker. Treebanks may optionally use nmod:poss to distinguish non-adpositional possessives.
    An appos is a nominal phrase that follows the head of another nominal phrase and stands in a co-reference or other equivalence relation to it.
    An amod is an adjective modifying the head of a nominal phrase.
    A nummod is a numeral modifying the head of a nominal phrase.
    An acl is a clause modifying the head of a nominal phrase, with the relative clause acl:relcl as an important subtype."""
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0
    dep_rels = [token.deprel for token in sentence.tokens]
    pre, post = 0, 0

    for i in range(len(dep_rels)):
        if dep_rels[i] in ['nmod','appos','nummod','advmod','discourse','amod']:
            if i+1 < heads[i+1]:
                pre += 1
            elif i+1 > heads[i+1]:
                post += 1
            else:
                print('Error')
    if pre_mod:
        return pre, len(dep_rels)
        #return 1000 / len(dep_rels) * pre
    if post_mod:
        return post, len(dep_rels)
        #return 1000 / len(dep_rels) * post
    return pre+post, len(dep_rels)
    #return 1000 / len(dep_rels) * (pre+post)

def find_children(heads, i): #find all children that have i as their direct or indirect head.
    children = []
    while i in heads:
        child = heads.index(i)
        children.append(child)
        heads[heads.index(i)] = None
        for c in find_children(heads, child):
            children.append(c)
    return children

def sub_incsc(sentence):
    """
    including four types:
    1 Clausal subjects(csubj)
    2 Clausal complements(objects), divided into those with obligatory control(xcomp) and those without(ccomp)
    3 Adverbial clause modifers(advcl)
    4 Adnominal clause modifiers(acl) (with relative clause as an important subtype in many languages)
    see https://universaldependencies.org/u/overview/complex-syntax.html#subordination
    """
  
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0
    dep_rels = [token.deprel for token in sentence.tokens]
    sub = set()

    for index in range(len(dep_rels)):
        if dep_rels[index] in ['csubj','xcomp','ccomp','advcl','acl','acl:relcl', 'acl:rel']:
            children = find_children(heads, index+1)
            for child in children:
                sub.add(child)
    return len(sub), len(dep_rels)
    #return 1000 / len(dep_rels) * len(sub)

def relative_incsc(sentence):
    """A relative clause is an instance of acl,
    characterized by finiteness and usually omission of the modified noun in the embedded clause.
    Some languages use a language-particular subtype acl:relcl
    for the traditional class of relative clauses."""
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0
    dep_rels = [token.deprel for token in sentence.tokens]
    rel = set()
    for index in range(len(dep_rels)):
        if re.search(r"rel", dep_rels[index]):
            rel.add(index+1)
            children = find_children(heads, index+1)
            for child in children:
                rel.add(child)

    return len(rel), len(dep_rels)
    #return 1000 / len(dep_rels) * len(rel)

def prep_incsc(sentence):
    heads = dep_heads_helper(sentence)
    if not heads:
        return 0.0
    dep_rels = [token.deprel for token in sentence.tokens]
    pp = set()
    for index in range(len(dep_rels)):
        if dep_rels[index] == 'case':
            heads_copy = deepcopy(heads)
            pp.add(heads[index+1])
            children = find_children(heads_copy, heads[index+1])
            for child in children:
                pp.add(child)

    return len(pp), len(dep_rels)
    #return 1000 / len(dep_rels) * len(pp)

def left_dep_ratio(text, left_count=False):
    left, total = 0, 0
    left_list = []
    for sentence in text.sentences:
        l, t = dep_dir_count(sentence, "left")
        left += l
        total += t
        if left_count:
            left_list.append(l)
    if left_count:
        return left_list
    if total:
        return round(left/float(total), 2)
    else:
        return 0.0

def right_dep_ratio(text, right_count=False):
    right, total = 0, 0
    right_list = []
    for sentence in text.sentences:
        r, t = dep_dir_count(sentence, "right")
        right += r
        total += t
        if right_count:
            right_list.append(r)
    if right_count:
        return right_list
    if total:
        return round(right/float(total), 2)
    else:
        return 0.0

def max_deparc(sentence):
    return max([token.dep_length for token in sentence.tokens])

def dep_length_total(sentence, average=False):
    if average:
        dep_lengths = [token.dep_length for token in sentence.tokens]
        return mean(dep_lengths), median(dep_lengths)
    return sum([token.dep_length for token in sentence.tokens])


class Syntactic_features:
    """all syntactic features are based on successful sentence parsing"""
    def __init__(self, content, algorithm='', level='sent'):
        functions = [
            ('Dependency length', dep_length_total, {}, 'one', 'sum'),                  #Sum
            ('Dependency arcs longer than 5', arc5plus, {}, 'one', 'sum'),              #Sum
            ('Longest dependency length', max_deparc, {}, 'one', 'max'),                #Max Len
            ('Ratio of right dependency arcs', dep_dir_count, {'dir':'right', 'ratio':False}, 'two', 'cent'),
            ('Ratio of left dependency arcs', dep_dir_count, {'dir':'left', 'ratio':False}, 'two', 'cent'),
            ('Modifier variation', mod_incsc, {}, 'two', 'incsc'),                      #INCSC
            ('Pre-modifier INCSC',mod_incsc, {'pre_mod':True}, 'two', 'incsc'),         #INCSC
            ('Post-modifier INCSC', mod_incsc, {'post_mod':True}, 'two', 'incsc'),      #INCSC
            ('Subordinate INCSC', sub_incsc, {}, 'two', 'incsc'),                       #INCSC
            ('Relative clause INCSC', relative_incsc, {}, 'two', 'incsc'),              #INCSC
            ('Prepositional complement INCSC', prep_incsc, {}, 'two', 'incsc'),          #INCSC
        ]

        self.feats = OrderedDict()
        self.sent_raw = OrderedDict()        
        self.empty = False
        if level == 'sent':
            self.ud_tree = content.ud_tree
            if not content.ud_tree:
                self.empty = True
        elif level in ['text', 'para']: #to choose sentences that are successfully parsed
            content = [sent for sent in content.sentences if sent.ud_tree]
            if not content:
                self.empty = True
        
        elif level == 'texts':
            content = [text for text in content if eval_str(text.syntactic)['empty'] == False]
            if not content:
                self.empty = True
        
        if not self.empty:
            if algorithm == '':
                for name, func, kwarg, args, incsc in functions:
                    if args == 'one':
                        if level == 'sent':
                            if name == 'Dependency length':
                                mean_scalar, median_scalar = func(content, average=True)
                                self.feats['$'.join([name, 'average'])] = {'mean':mean_scalar, 'median':median_scalar}
                            scalar = func(content, **kwarg)
                            self.feats[name] = scalar

                        elif level in ['para', 'text']:
                            sent_scalars = []
                            for sent in content:
                                sent_scalars.append(eval_str(sent.syntactic)['feats'][name])
                            self.feats[name] = sum(sent_scalars) if incsc == 'sum' else max(sent_scalars)
                            self.sent_raw[name] = sent_scalars
                        
                        elif level == 'texts':
                            text_scalars = []
                            for text in content:
                                text_scalars.append(eval_str(text.syntactic)['feats'][name])
                            self.feats[name] = sum(text_scalars) if incsc == 'sum' else max(text_scalars)

                    elif args == 'two':
                        if level == 'sent':
                            c, t = func(content, **kwarg)
                        
                        elif level in ['para', 'text']:
                            c, t, sent_scalars = 0,0, []
                            for sent in content:
                                sc, st = eval_str(sent.syntactic)['sent_raw']['$'.join([name, 'raw'])]
                                c += sc
                                t += st
                                sent_scalars.append(eval_str(sent.syntactic)['feats'][name])
                            self.sent_raw[name] = sent_scalars
                        
                        elif level == 'texts':
                            c, t = 0, 0
                            for text in content:
                                sc, st = eval_str(text.syntactic)['sent_raw']['$'.join([name, 'raw'])]
                                c += sc
                                t += st

                        if incsc == 'cent':
                            scalar = round(c/t*100, 2)
                        elif incsc == 'incsc':
                            scalar = round(c/t*1000, 2) if t else 1000 #set 1000 as the ceiling
                        
                        self.feats[name] = scalar
                        self.sent_raw['$'.join([name, 'raw'])] = c, t

            elif algorithm == 'average':
                for name, _, _, args, _ in functions:
                    values = [] 
                    if level != 'texts':
                        for sentence in content:
                            values.append(eval_str(sentence.syntactic)['feats'][name])
                        self.feats[name] = {'mean':mean(values), 'median':median(values)}
                    else:
                        for text in content:
                            values.extend(eval_str(text.syntactic)['sent_raw'][name])
                        self.feats[name] = {'mean':mean(values), 'median':median(values)}
                      


        


 
