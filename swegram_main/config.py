#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from datetime import timedelta

from datetime import datetime
import pytz
import os

from .models import TextStats

def get_text_names():
    return list(set([
      text.filename for text in TextStats.objects.all()
    ]))

def delete_old_texts():
    max_live_time = MAX_LIVE_TIME
    now = datetime.now()
    utc = pytz.UTC
    for text in TextStats.objects.all():
        if utc.localize(now) > (text.date_added + max_live_time):
            text.delete()
            if text.filename in get_text_names():
                try:
                    os.remove(os.path.join(OUTPUT_DIR, text.filename))
                except:
                    pass
                  
def automatic_delete():
    time_step = CLEANUP_TIME_STEP
    print(
      'The database will be clean up every %s seconds.' % (time_step.total_seconds()),
      'The texts stored in the database longer than %s days are to be deleted.' % (MAX_LIVE_TIME.days),
      'The annotated text is to be deleted if there is no live text instance with the same name exists.'
      )
    delete_old_texts()
    # return HttpResponse('''
    #   The database will be clean up every %s seconds.
    #   The texts stored in the database longer than %s days are to be deleted.
    #   The annotated text is to be deleted if there is no live text instance with the same name exists.
    #   '''% (time_step.total_seconds(), config.MAX_LIVE_TIME.days))

UPLOAD_LOCATION = settings.BASE_DIR + "/swegram_main/uploads/"
PIPE_PATH       = settings.BASE_DIR + "/local/swegram/django/swegram/swegram_main/annotate/pipeline/"

MAX_LIVE_TIME = timedelta(days=7) #the time the texts can be stored in the database
CLEANUP_TIME_STEP = timedelta(days=1) #after period the system clear up the olds from the database

# The output path and file names for download

OUTPUT_DIR = settings.BASE_DIR + '/swegram_main/handle_texts/pipeline/output/' #need to be put into config.py
OUT_FILE = 'text_file'   
OUT_STATS_FILE = 'stats_file' 

PAGE_SIZE = 10 # the default page size is 10 items

COLUMN_DELIMITER = '¥' # This will be used to separate different columns in uploaded csv file
METADATA_DELIMITER = ' '
METADATA_INITIAL = '<'
METADATA_FINAL = '>'
METADATA_DELIMITER_LEBAL = ' '
METADATA_DELIMITER_TAG = ':'

NO_METADATA_STRING = '(ingen metadata)' # metadata is printed when there is, no prompt when the text does not contain metadata

UD_TAGS = [
            'ADJ',
            'ADP',
            'ADV',
            'AUX',
            'CCONJ',
            'DET',
            'INTJ',
            'NOUN',
            'NUM',
            'PART',
            'PRON',
            'PROPN',
            'PUNCT',
            'SCONJ',
            'SYM',
            'VERB',
            'X',
]

SUC_TAGS = [
            'AB',
            'DT',
            'HA',
            'HD',
            'HP',
            'HS',
            'IE',
            'IN',
            'JJ',
            'KN',
            'NN',
            'PC',
            'PL',
            'PM',
            'PN',
            'PP',
            'PS',
            'RG',
            'RO',
            'SN',
            'UO',
            'VB',
            'MAD', #Why does these three tags not included in suc tags.
            'MID',
            'PAD'
]


#Penn Treebank tagset is used as xpos for English.
#We retreieve the tagset from the following link: https://ufal.mff.cuni.cz/pdt/Morphology_and_Tagging/Doc/PTTags.pdf
PT_TAGS = [
    'AFX', # see info from https://catalog.ldc.upenn.edu/docs/LDC2007T02/pos-guidelines-addenda.txt
    'CC',
    'CD',
    'DT',
    'EX',
    'FW',
    'HYPH',# see info from https://catalog.ldc.upenn.edu/docs/LDC2007T02/pos-guidelines-addenda.txt
    'IN',
    'JJ',
    'JJR',
    'JJS',
    'LS',
    'MD',
    'NN',
    'NNS',
    'NNP',  # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    'NNPS', # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    'NP',
    'NPS',
    'PDT',
    'POS',
    'PRP',  # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    'PRP$', # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    'PPS',  # unknown
    'PP$',
    'RB',
    'RBR',
    'RBS',
    'RP',
    'SYM',
    'TO',
    'UH',
    'VB',
    'VBD',
    'VBG',
    'VBN',
    'VBP',
    'VBZ',
    'WDT',
    'WP',
    'WP$',
    'WRB',
    '#',
    '$',
    '.',
    ',',
    ':',
    '(',
    ')',
    '"',            #straight double quote
    chr(8216),      #left open single quote
    chr(8220),      #left open double quote
    chr(8217),      #right close single quote
    chr(8221)       #right close double quote
]


DEPRELS = [
    'acl',          # clausal modifier of noun (adnominal clause)
    'acl:relcl',    # relative clause modifier
    'advcl',        # adverbial clause modifier
    'advmod',       # adverbial modifier
    'advmod:emph',  # emphasizing word, intensifier
    'advmod:lmod',  # locative adverbial modifier
    'amod',         # adjectival modifier
    'appos',        # appositional modifier
    'aux',          # auxiliary
    'aux:pass',     # passive auxiliary
    'case',         # case marking
    'cc',           # coordinating conjunction
    'cc:preconj',   # preconjunct
    'ccomp',        # clausal complement
    'clf',          # classifier
    'compound',     # compound
    'compound:lvc', # light verb construction
    'compound:prt', # phrasal verb particle
    'compound:redup',# reduplicated compounds
    'compound:svc', # serial verb compounds
    'conj',         # conjunct
    'cop',          # copula
    'csubj',        # clausal subject
    'csubj:pass',   # clausal passive subject
    'dep',          # unspecified dependency
    'det',          # determiner
    'det:numgov',   # pronominal quantifier governing the case of the noun
    'det:nummod',   # pronominal quantifier agreeing in case with the noun
    'det:predet',   #
    'det:poss',     # possessive determiner
    'discourse',    # discourse element
    'dislocated',   # dislocated elements
    'expl',         # expletive
    'expl:impers',  # impersonal expletive
    'expl:pass',    # reflexive pronoun used in reflexive passive
    'expl:pv',      # reflexive clitic with an inherently reflexive verb
    'fixed',        # fixed multiword expression
    'flat',         # flat multiword expression
    'flat:foreign', # foreign words
    'flat:name',    # names
    'goeswith',     # goes with
    'iobj',         # indirect object
    'list',         # list
    'mark',         # marker
    'nmod',         # nominal modifier
    'nmod:poss',    # possessive nominal modifier
    'nmod:tmod',    # temporal modifier
    'nsubj',        # nominal subject
    'nsubj:pass',   # passive nominal subject
    'nummod',       # numeric modifier
    'nummod:gov',   # numeric modifier governing the case of the noun
    'obj',          # object
    'obl',          # oblique nominal
    'obl:agent',    # agent modifier
    'obl:arg',      # oblique argument
    'obl:lmod',     # locative modifier
    'obl:tmod',     # temporal modifier
    'obl:npmod',    # 
    'orphan',       # orphan
    'parataxis',    # parataxis
    'punct',        # punctuation
    'reparandum',   # overridden disfluency
    'root',         # root
    'vocative',     # vocative
    'xcomp',        # open clausal complement   
]

# the ufeats below are extracted from annotation of europarl corpus with previous 100M
UFEATS = [
    '-',
    'AKT',
    'AN',
    'DEF',
    'GEN',
    'IMP',
    'IND',
    'IND/DEF',
    'INF',
    'KOM',
    'KON',
    'MAS',
    'NEU',
    'NOM',
    'OBJ',
    'PLU',
    'POS',
    'PRF',
    'PRS',
    'PRT',
    'SFO',
    'SIN',
    'SIN/PLU',
    'SMS',
    'SUB',
    'SUB/OBJ',
    'SUP',
    'SUV',
    'UTR',
    'UTR/NEU',
    '_',
]

# the feats below are extracted from annotation of europarl corpus with previous 100M
# the default is _
# FEATS = {
#     'Case':['Nom','Gen','Acc'],
#     'Definite':['Ind','Def'],
#     'Gender':['Neut','Com','Masc'],
#     'Number':['Sing','Plur'],
#     'Mood':['Ind','Sub','Imp'],
#     'Tense':['Pres','Past'],
#     'VerbForm':['Fin','Part','Inf','Sup'],
#     'Voice':['Act','Pass'],
#     'Degree':['Pos','Sup','Cmp'],
#     'Polarity':['Neg'],
#     'Poss':['Yes'],
#     'PronType':['Int','Rel'],
#     'Abbr':['Yes'],
#     'Foreign':['Yes']
# }

# the feats below are extacted from https://universaldependencies.org/u/feat/index.html
FEATS = {
  'PronType': ['Art', 'Int,Rel', 'Dem', 'Emp', 'Exc', 'Ind', 'Int', 'Neg', 'Prs', 'Rcp', 'Rel', 'Tot'],
  'NumType': ['Card', 'Dist', 'Frac', 'Mult', 'Ord', 'Range', 'Sets'],
  'Poss': ['Yes'],
  'Reflex': ['Yes'],
  'Foreign': ['Yes'],
  'Abbr': ['Yes'],
  'Typo': ['Yes'],
  'Gender': ['Com', 'Fem', 'Masc', 'Neut'],
  'Animacy': ['Anim', 'Hum', 'Inan', 'Nhum'],
  'Number': ['Coll', 'Count', 'Dual', 'Grpa', 'Grpl', 'Inv', 'Pauc', 'Plur', 'Ptan', 'Sing', 'Tri'],
  'Case': ['Abs', 'Abe', 'Ben', 'Cau', 'Cmp', 'Abl', 'Add', 'Ade', 'All', 'Acc', 'Cns', 'Com', 'Dat', 'Dis', 'Del', 'Ela', 'Ess', 'Ill', 'Erg', 'Equ', 'Gen', 'Ins', 'Ine', 'Lat', 'Loc', 'Nom', 'Par', 'Tem', 'Tra', 'Voc', 'Per', 'Sub', 'Sup', 'Ter'],
  'Definite': ['Com', 'Cons', 'Def', 'Ind', 'Spec'],
  'Degree': ['Abs', 'Cmp', 'Equ', 'Pos', 'Sup'],
  'VerbForm': ['Conv', 'Fin', 'Gdv', 'Ger', 'Inf', 'Part', 'Sup', 'Vnoun'],
  'Mood': ['Adm', 'Cnd', 'Des', 'Imp', 'Ind', 'Irr', 'Jus', 'Nec', 'Opt', 'Pot', 'Prp', 'Qot', 'Sub'],
  'Tense': ['Fut', 'Imp', 'Past', 'Pqp', 'Pres'],
  'Aspect': ['Hab', 'Imp', 'Iter', 'Perf', 'Prog', 'Prosp'],
  'Voice': ['Act', 'Antip', 'Bfoc', 'Cau', 'Dir', 'Inv', 'Lfoc', 'Mid', 'Pass', 'Rcp'],
  'Evident': ['Fh', 'Nfh'],
  'Polarity': ['Neg', 'Pos'],
  'Person': ['0', '1', '2', '3', '4'],
  'Polite': ['Elev', 'Form', 'Humb', 'Infm'],
  'Clusivity': ['Ex', 'In'],
}

"""
import threading
import time

class Thread_delete_old_texts(threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting Thread " + self.name)
        # Get lock to synchronize threads
        while True:
            threadLock.acquire()
            automatic_delete()
            threadLock.release()
            print('Text deletion is updated at %s. Next automatic deletion occurs in %s.' % (time.ctime(time.time()), str(CLEANUP_TIME_STEP)))
            time.sleep(CLEANUP_TIME_STEP.total_seconds())

threadLock = threading.Lock()
thread_delete_old_texts = Thread_delete_old_texts(1, "Thread-delete-old-texts")
thread_delete_old_texts.start()
"""
