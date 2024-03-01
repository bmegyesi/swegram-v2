import json
from pathlib import Path
from typing import Dict, TypeVar


K = TypeVar("K", float, str)


def _json_load(filename: Path) -> Dict[str, K]:
    with open(filename, mode="r", encoding="utf-8") as json_file:
        return json.load(json_file)


BASE_DIR = Path(__file__).absolute().parent.parent
TOOL_DIR = BASE_DIR.joinpath("tools")

EFSELAB_DIR = TOOL_DIR.joinpath("efselab")
EFSELAB = EFSELAB_DIR.joinpath("swe_pipeline.py")

UDPIPE_BASE = TOOL_DIR.joinpath("udpipe")
UDPIPE = UDPIPE_BASE.joinpath("udpipe")
UDPIPE_MODEL = UDPIPE_BASE.joinpath("en", "english-ud-2.0-170801.udpipe")

HISTNORM_EN = "histnorm"
HISTNORM_SV = TOOL_DIR.joinpath("HistNorm")


# Lexical feature related variables
KELLY_DIR = BASE_DIR.joinpath("swegram_main", "statistics", "kelly")
KELLY_EN = _json_load(KELLY_DIR.joinpath("kelly.en"))
KELLY_SV = _json_load(KELLY_DIR.joinpath("kelly.sv"))
WPM_SV = _json_load(KELLY_DIR.joinpath("wpm.sv"))
ADVANCE_CEFR_LEVELS = "3456"  # WHICH CEFR LEVELS ARE TREATED AS BEING ADVANCE


# Syntactical feature related variables
LONG_ARC_THRESHOLD = 5
MODIFIER_DEPREL_LABELS = [
  "advmod",  # adverbial modifier
  "amod",  # adjective modifier
  "appos",  # appositional modifier
  "discourse",  # discourse element
  "nmod",  # nominal modifier
  "nummod",  # numeric modifier
]
# See https://universaldependencies.org/u/overview/complex-syntax.html#subordination
SUBORDINATION_DEPREL_LABELS = [
  "acl",  # Adnominal clause modifiers
  "advcl",  # Adverbial clause modifiers
  "ccomp",  # Clausal complements (objects) without obligatory control
  "csubj",  # Clausal subjects 
  "xcomp",  # Clausal complements (objects) with obligatory control
]


# Variables for statistics
UNITS = ["corpus", "text", "paragraph", "sentence"]
ASPECTS = ["general", "readability", "morph", "lexical", "syntactic"]


PAGE_SIZE = 10 # the default page size is 10 items


COLUMN_DELIMITER = ","
METADATA_INITIAL = "<"
METADATA_FINAL = ">"
EMPTY_METADATA = f"{METADATA_INITIAL}{METADATA_FINAL}"
METADATA_DELIMITER_LEBAL = ";"
METADATA_DELIMITER_TAG = ":"


AGGREGATION_CONLLS = "aggregation.conll"
JSON_CONLL_CORPUS_KEY = "Corpus"
JSON_CONLL_METADATA_KEY = "metadata"
JSON_CONLL_TEXT_KEY = "text"
XLSX_CONLL_SHEET_PREFIX = "text"


UD_TAGS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ",
           "DET", "INTJ", "NOUN", "NUM", "PART",
           "PRON", "PROPN", "PUNCT", "SCONJ",
           "SYM", "VERB", "X"]

SUC_TAGS = ["AB", "DT", "HA", "HD", "HP", "HS", "IE", "IN",
            "JJ", "KN", "NN", "PC", "PL", "PM", "PN", "PP",
            "PS", "RG", "RO", "SN", "UO", "VB",
            "MAD", #Why does these three tags not included in suc tags.
            "MID", "PAD"]


#Penn Treebank tagset is used as xpos for English.
#We retreieve the tagset from the following link: https://ufal.mff.cuni.cz/pdt/Morphology_and_Tagging/Doc/PTTags.pdf
PT_TAGS = ["AFX", # see info from https://catalog.ldc.upenn.edu/docs/LDC2007T02/pos-guidelines-addenda.txt
           "CC", "CD", "DT", "EX", "FW",
           "HYPH",  # see info from https://catalog.ldc.upenn.edu/docs/LDC2007T02/pos-guidelines-addenda.txt
           "IN", "JJ", "JJR", "JJS", "LS",
           "MD", "NN", "NNS",
           "NNP",  # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
           "NNPS", # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
           "NP", "NPS", "PDT", "POS",
           "PRP",  # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
           "PRP$", # see https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
           "PPS",  # unknown
           "PP$", "RB", "RBR", "RBS", "RP", "SYM", "TO",
           "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
           "WDT", "WP", "WP$", "WRB", "#", "$", ".", ",",
           ":", "(", "-LRB-", ")", "-RRB-", "''", "``", "\"",  #straight double quote
           chr(8216),      #left open single quote
           chr(8220),      #left open double quote
           chr(8217),      #right close single quote
           chr(8221)       #right close double quote
]


DEPRELS = [
    "acl",          # clausal modifier of noun (adnominal clause)
    "acl:relcl",    # relative clause modifier
    "advcl",        # adverbial clause modifier
    "advmod",       # adverbial modifier
    "advmod:emph",  # emphasizing word, intensifier
    "advmod:lmod",  # locative adverbial modifier
    "amod",         # adjectival modifier
    "appos",        # appositional modifier
    "aux",          # auxiliary
    "aux:pass",     # passive auxiliary
    "case",         # case marking
    "cc",           # coordinating conjunction
    "cc:preconj",   # preconjunct
    "ccomp",        # clausal complement
    "clf",          # classifier
    "compound",     # compound
    "compound:lvc", # light verb construction
    "compound:prt", # phrasal verb particle
    "compound:redup",# reduplicated compounds
    "compound:svc", # serial verb compounds
    "conj",         # conjunct
    "cop",          # copula
    "csubj",        # clausal subject
    "csubj:pass",   # clausal passive subject
    "dep",          # unspecified dependency
    "det",          # determiner
    "det:numgov",   # pronominal quantifier governing the case of the noun
    "det:nummod",   # pronominal quantifier agreeing in case with the noun
    "det:predet",   #
    "det:poss",     # possessive determiner
    "discourse",    # discourse element
    "dislocated",   # dislocated elements
    "expl",         # expletive
    "expl:impers",  # impersonal expletive
    "expl:pass",    # reflexive pronoun used in reflexive passive
    "expl:pv",      # reflexive clitic with an inherently reflexive verb
    "fixed",        # fixed multiword expression
    "flat",         # flat multiword expression
    "flat:foreign", # foreign words
    "flat:name",    # names
    "goeswith",     # goes with
    "iobj",         # indirect object
    "list",         # list
    "mark",         # marker
    "nmod",         # nominal modifier
    "nmod:poss",    # possessive nominal modifier
    "nmod:tmod",    # temporal modifier
    "nsubj",        # nominal subject
    "nsubj:pass",   # passive nominal subject
    "nummod",       # numeric modifier
    "nummod:gov",   # numeric modifier governing the case of the noun
    "obj",          # object
    "obl",          # oblique nominal
    "obl:agent",    # agent modifier
    "obl:arg",      # oblique argument
    "obl:lmod",     # locative modifier
    "obl:tmod",     # temporal modifier
    "obl:npmod",    # 
    "orphan",       # orphan
    "parataxis",    # parataxis
    "punct",        # punctuation
    "reparandum",   # overridden disfluency
    "root",         # root
    "vocative",     # vocative
    "xcomp",        # open clausal complement   
]

# the ufeats below are extracted from annotation of europarl corpus with previous 100M
XFEATS = ["-", "AKT", "AN", "DEF", "GEN", "IMP", "IND", "IND/DEF", "INF",
          "KOM", "KON", "MAS", "NEU", "NOM", "OBJ", "PLU", "POS", "PRF",
          "PRS", "PRT", "SFO", "SIN", "SIN/PLU", "SMS", "SUB", "SUB/OBJ",
          "SUP", "SUV", "UTR", "UTR/NEU", "_"]

# the feats below are extacted from https://universaldependencies.org/u/feat/index.html
FEATS = {
  "PronType": ["Art", "Int,Rel", "Dem", "Emp", "Exc", "Ind", "Int", "Neg", "Prs", "Rcp", "Rel", "Tot"],
  "NumType": ["Card", "Dist", "Frac", "Mult", "Ord", "Range", "Sets"],
  "Poss": ["Yes"],
  "Reflex": ["Yes"],
  "Foreign": ["Yes"],
  "Abbr": ["Yes"],
  "Typo": ["Yes"],
  "Gender": ["Com", "Fem", "Masc", "Neut"],
  "Animacy": ["Anim", "Hum", "Inan", "Nhum"],
  "Number": ["Coll", "Count", "Dual", "Grpa", "Grpl", "Inv", "Pauc", "Plur", "Ptan", "Sing", "Tri"],
  "Case": ["Abs", "Abe", "Ben", "Cau", "Cmp", "Abl", "Add", "Ade", "All", "Acc", "Cns", "Com", "Dat", "Dis", "Del", "Ela", "Ess", "Ill", "Erg", "Equ", "Gen", "Ins", "Ine", "Lat", "Loc", "Nom", "Par", "Tem", "Tra", "Voc", "Per", "Sub", "Sup", "Ter"],
  "Definite": ["Com", "Cons", "Def", "Ind", "Spec"],
  "Degree": ["Abs", "Cmp", "Equ", "Pos", "Sup"],
  "VerbForm": ["Conv", "Fin", "Gdv", "Ger", "Inf", "Part", "Sup", "Vnoun"],
  "Mood": ["Adm", "Cnd", "Des", "Imp", "Ind", "Irr", "Jus", "Nec", "Opt", "Pot", "Prp", "Qot", "Sub"],
  "Tense": ["Fut", "Imp", "Past", "Pqp", "Pres"],
  "Aspect": ["Hab", "Imp", "Iter", "Perf", "Prog", "Prosp"],
  "Voice": ["Act", "Antip", "Bfoc", "Cau", "Dir", "Inv", "Lfoc", "Mid", "Pass", "Rcp"],
  "Evident": ["Fh", "Nfh"],
  "Polarity": ["Neg", "Pos"],
  "Person": ["0", "1", "2", "3", "4"],
  "Polite": ["Elev", "Form", "Humb", "Infm"],
  "Clusivity": ["Ex", "In"],
}
