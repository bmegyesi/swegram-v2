
from collections import Counter
from pathlib import Path
from typing import Tuple, List, Union, Iterator

from swegram_main.pipeline.lib.utils import read
from swegram_main.config import UD_TAGS, PT_TAGS, SUC_TAGS, DEPRELS, XFEATS, FEATS


class UploadedTextValidationError(Exception):
    """Uploaded text validation error"""


class Checker:
    """Check syntax from uploaded file"""

    def __init__(self, filepath: Path):
        context = read(filepath)


def check_line(line: str, index: str, text_index: str, model: str) -> Tuple[bool, bool, bool, List[str]]:
    errors = []
    reference = f"[Line Reference: {text_index} {index}]"
    # split the columns given the model
    if model.lower() == "efselab":
        ti, i, token, norm, _, upos_tag, xpos_tag, ud_features, suc_features, head, deprel, *_ = line.split('\t')
    
    elif model.lower() == "udpipe":
        ti, i, token, norm, _, upos_tag, xpos_tag, ud_features, head, deprel, *_ = line.split('\t')

    else:
        raise UploadedTextValidationError(f"Unknown model: {model}")

    # check format for each column
    if ti != text_index:
        errors.append(f"{reference} COLUMN_INDEX_ERROR: Expected to get {text_index}, but got {ti}")
    if i != index:
        errors.append(f"{reference} COLUMN_INDEX_ERROR: Expected to get {index}, but got {i}")

    normalized = True if token == '_' or norm != '_' else False

    tagged = True if upos_tag != '_' and xpos_tag != '_' else False
    if tagged:
        parsed = True if head != '_' and deprel != '_' else False
        if upos_tag not in UD_TAGS:
            errors.append(f"{reference} COLUMN_UPOS_ERROR: Unknown upos {upos_tag}")

        if model.lower() == "efselab":
            if xpos_tag not in SUC_TAGS:
                errors.append(f"{reference} COLUMN_XPOS_ERROR: Unknown xpos {xpos_tag}")
            for suc_feat in suc_features.split('|'):
                if suc_feat not in XFEATS:
                    errors.append(f"{reference} COLUMN_XFEAT_ERROR: Unknown xfeat: {suc_feat}")
        else:
            if xpos_tag not in PT_TAGS:
                errors.append(f"{reference} COLUMN_XPOS_ERROR: Unknown xpos {xpos_tag}")

        if ud_features != '_':
            for ud_feat in ud_features.split('|'):
                ud_feat_key, ud_feat_value = ud_feat.split('=', maxsplit=1)
                if ud_feat_key not in FEATS or ud_feat_value not in FEATS[ud_feat_key]:
                    errors.append(f"{reference} COLUMN_FEAT_ERROR: Unknown ufeat: {ud_feat_key}={ud_feat_value}")

        if parsed and deprel not in DEPRELS:
            errors.append(f"{reference} COLUMN_DEPREL_ERROR: Unknown deprel {deprel}")
        if parsed and not head.isdigit():
            errors.append(f"{reference} COLUMN_HEAD_ERROR: Expected to have digit, but got {head}")
    else:
        parsed = False
    
    return normalized, tagged, parsed, head, errors


def check_sentence(model: str, word_list: List[str], text_index: str):

    normalized, tagged, parsed, heads, errors = [], [], [], [], []
    for index, word_line in enumerate(word_list, 1):
        _normalized, _tagged, _parsed, head, _messages = check_line(word_line, str(index), text_index, model)
        normalized.append(_normalized)
        tagged.append(_tagged)
        parsed.append(_parsed)
        heads.append(head)
        errors.extend(_messages)
    if all(parsed):
        is_ud_tree_or_error = is_a_ud_tree(heads, f"[Sentence Reference: {text_index}]")
        if is_ud_tree_or_error is not True:
            parsed = False
            errors.append(is_ud_tree_or_error)
    else:
        parsed = False
    return all(normalized), all(tagged), parsed, errors


def check_text(model: str, text: Iterator) -> None:
    """Check uploaded text if it is normalized, tagged or parsed, and check if there is any format error
    """
    newlines = 0
    p_index, s_index = 1, 1
    sentence = []
    line = next(text)
    normalized, tagged, parsed, errors = [], [], [], []
    try:
        while True:
            if line.strip():
                sentence.append(line)
            elif line == '\n':
                if sentence:
                    _normalized, _tagged, _parsed, _errors = check_sentence(model, sentence, f"{p_index}.{s_index}")
                    normalized.append(_normalized)
                    tagged.append(_tagged)
                    parsed.append(_parsed)
                    errors.extend(_errors)
                    s_index += 1
                    newlines = 1
                    sentence = []
                else:
                    if newlines == 1:
                        p_index += 1
                        s_index = 1
                    newlines += 1
            line = next(text)
    except StopIteration:
        print("Process checking uploaded text done.")

    if errors:
        raise UploadedTextValidationError('\n'.join(errors))
    return any(normalized), any(tagged), any(parsed)


def is_a_ud_tree(heads: List[str], error_prefix: str = "") -> Union[bool, str]:
    heads = list(map(int, heads))
    children = list(range(1,len(heads)+1))
    if 0 not in heads:
        return f"{error_prefix} Root is missing."
    if Counter(heads)[0] > 1:
        return f"{error_prefix} More than one roots in sentence"
    if len(children) > len(set(children)):
        return f"{error_prefix} Same indeces for two nodes in sentence."

    for i in children:
        head = [heads[i - 1]]
        while 0 not in head:
            if heads[head[-1] - 1] in head:
                return f"{error_prefix} Cycle Error in sentence."
            head.append(heads[head[-1] - 1])
        head = []
    return True


# text_path = Path("/tmp/test/10-sv_0.conll")
# check_text("efselab", read(text_path))