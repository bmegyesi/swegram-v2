
sv_text = "/home/rruan1/swegram_dev/swegram/tests/integrations/10-sv.txt"
en_text = "/home/rruan1/swegram_dev/swegram/tests/integrations/10-en.txt"

import os
import tempfile
import hashlib
from pathlib import Path

import pytest
from swegram_main.pipeline import pipeline
from swegram_main.pipeline.pipeline import Text, restore, run, text_postprocess, annotate


histnorm_model_sv = "histnorm_sv"
histnorm_model_en = "histnorm_en"
efselab = "efselab"
udpipe = "udpipe"
resources_path = Path("/home/rruan1/swegram_dev/swegram/tests/resources")
sv_norm_conll = "10-sv-norm.conll"
sv_norm_tag = "10-sv-norm.tag"
sv_conll = "10-sv.conll"
sv_tag = "10-sv.tag"
sv_spell = "10-sv.spell"
sv_tok = "10-sv.tok"

en_norm_conll = "10-en-norm.conll"
en_norm_tag = "10-en-norm.tag"
en_conll = "10-en.conll"
en_tag = "10-en.tag"
en_spell = "10-en.spell"
en_tok = "10-en.tok"


def get_md5(filepath: Path) -> None:
    with open(filepath, "rb") as input_file:
        return hashlib.md5(input_file.read()).hexdigest()

def get_md5_without_comments(filepath: Path) -> None:
    with open(filepath, "r") as input_file:
        lines = [line for line in input_file.readlines() if not line.startswith("#")]
        return hashlib.md5("\n".join(lines).encode()).hexdigest()


######################################################
# md5 values for the given target texts (swedish)    #
######################################################
@pytest.fixture(scope="module", name="sv_conll_md5")
def sv_conll_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_conll))


@pytest.fixture(scope="module", name="sv_conll_norm_md5")
def sv_conll_norm_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_norm_conll))


@pytest.fixture(scope="module", name="sv_tag_md5")
def sv_tag_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_tag))


@pytest.fixture(scope="module", name="sv_tag_norm_md5")
def sv_tag_norm_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_norm_tag))


@pytest.fixture(scope="module", name="sv_spell_md5")
def sv_spell_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_spell))


@pytest.fixture(scope="module", name="sv_tok_md5")
def sv_tok_md5_fixture():
    yield get_md5(resources_path.joinpath(sv_tok))

######################################################
# md5 values for the given target texts (english)    #
######################################################
@pytest.fixture(scope="module", name="en_conll_md5")
def en_conll_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_conll))


@pytest.fixture(scope="module", name="en_conll_norm_md5")
def en_conll_norm_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_norm_conll))


@pytest.fixture(scope="module", name="en_tag_md5")
def en_tag_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_tag))


@pytest.fixture(scope="module", name="en_tag_norm_md5")
def en_tag_norm_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_norm_tag))


@pytest.fixture(scope="module", name="en_spell_md5")
def en_spell_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_spell))


@pytest.fixture(scope="module", name="en_tok_md5")
def en_tok_md5_fixture():
    yield get_md5_without_comments(resources_path.joinpath(en_tok))


######################################################
@pytest.fixture(scope="function", name="temp")
def temp_fixture():
    yield tempfile.TemporaryDirectory()


@pytest.fixture(scope="function", name="sv")
def sv_fixture():
    yield Path(sv_text)


@pytest.fixture(scope="function", name="sv_pipe")
def sv_pipe_fixture(temp, sv):
    yield pipeline.Pipeline(sv, output_dir=Path(temp.name))


@pytest.fixture(scope="function", name="en")
def en_fixture():
    yield Path(en_text)


@pytest.fixture(scope="function", name="en_pipe")
def en_pipe_fixture(temp, en):
    yield pipeline.Pipeline(en, output_dir=Path(temp.name))


######################################################
#            annotation component path               #
######################################################
@pytest.fixture(scope="function", name="tok")
def tok_fixture(temp, sv):
    yield Path(os.path.join(temp.name, f"{sv.stem}_0.tok"))


@pytest.fixture(scope="function", name="spell")
def spell_fixture(temp, sv):
    yield Path(os.path.join(temp.name, f"{sv.stem}_0.spell"))


@pytest.fixture(scope="function", name="tag")
def tag_fixture(temp, sv):
    yield Path(os.path.join(temp.name, f"{sv.stem}_0.tag"))


@pytest.fixture(scope="function", name="sv_conll")
def sv_conll_fixture(temp, sv):
    yield Path(os.path.join(temp.name, f"{sv.stem}_0.conll"))


@pytest.fixture(scope="function", name="en_conll")
def en_conll_fixture(temp, en):
    yield Path(os.path.join(temp.name, f"{en.stem}_0.conll"))


######################################################
#      Test cases: annotate from raw texts           #
######################################################
def test_annotation_tokenize_efselab(sv_pipe, sv_conll, sv_tok_md5):
    sv_pipe.run(model=efselab, action="tokenize")
    assert sv_tok_md5 == get_md5(sv_conll)


def test_annotation_tokenize_udpipe(en_pipe, en_conll, en_tok_md5):
    en_pipe.run(model=udpipe, action="tokenize")
    assert en_tok_md5 == get_md5_without_comments(en_conll)


def test_annotation_normalize_efselab(sv_pipe, sv_conll, sv_spell_md5):
    sv_pipe.run(model=histnorm_model_sv, action="normalize")
    assert sv_spell_md5 == get_md5(sv_conll)


def test_annotation_normalize_udpipe(en_pipe, en_conll, en_spell_md5):
    en_pipe.run(model=histnorm_model_en, action="normalize")
    assert en_spell_md5 == get_md5_without_comments(en_conll)


def test_annotation_tag_efselab(sv_pipe, sv_conll, sv_tag_md5):
    sv_pipe.run(model=efselab, action="tag")
    assert sv_tag_md5 == get_md5(sv_conll)


def test_annotation_tag_udpipe(en_pipe, en_conll, en_tag_md5):
    en_pipe.run(model=udpipe, action="tag")
    assert en_tag_md5 == get_md5_without_comments(en_conll)


def test_annotation_parse_efselab(sv_pipe, sv_conll, sv_conll_md5):
    sv_pipe.run(model=efselab, action="parse")
    assert sv_conll_md5 == get_md5(sv_conll)


def test_annotation_parse_udpipe(en_pipe, en_conll, en_conll_md5):
    en_pipe.run(model=udpipe, action="parse")
    assert en_conll_md5 == get_md5_without_comments(en_conll)


def test_annotation_tag_efselab_with_normalization(sv_pipe, sv_conll, sv_tag_norm_md5):
    sv_pipe.run(model="histnorm_sv", action="normalize", post_action=False)
    sv_pipe.run(model=efselab, action="tag")
    assert sv_tag_norm_md5 == get_md5(sv_conll)


def test_annotation_tag_udpipe_with_normalization(en_pipe, en_conll, en_tag_norm_md5):
    en_pipe.run(model="histnorm_en", action="normalize", post_action=False)
    en_pipe.run(model=udpipe, action="tag")
    assert en_tag_norm_md5 == get_md5_without_comments(en_conll)


def test_annotation_parse_efselab_with_normalization(sv_pipe, sv_conll, sv_conll_norm_md5):
    sv_pipe.run(model="histnorm_sv", action="normalize", post_action=False)
    sv_pipe.run(model=efselab, action="parse")
    assert sv_conll_norm_md5 == get_md5(sv_conll)


def test_annotation_parse_udpipe_with_normalization(en_pipe, en_conll, en_conll_norm_md5):
    en_pipe.run(model="histnorm_en", action="normalize", post_action=False)
    en_pipe.run(model=udpipe, action="parse")
    assert en_conll_norm_md5 == get_md5_without_comments(en_conll)


######################################################
#      Fixtures: restore from annotated text         #
######################################################
@pytest.fixture(scope="function", name="restore_sv_tok_text_instance")
def restore_sv_tok_text_instance_fixture(temp):
    restore("tokenized", resources_path.joinpath("10-sv.tok"), Path(temp.name), efselab)
    yield Text(filepath=Path(temp.name).joinpath("10-sv.txt"))


@pytest.fixture(scope="function", name="restore_en_tok_text_instance")
def restore_en_tok_text_instance_fixture(temp):
    restore("tokenized", resources_path.joinpath("10-en.tok"), Path(temp.name), udpipe)
    yield Text(filepath=Path(temp.name).joinpath("10-en.txt"))


@pytest.fixture(scope="function", name="restore_sv_tag_text_instance")
def restore_sv_tag_text_instance_fixture(temp):
    restore("tagged", resources_path.joinpath("10-sv.tag"), Path(temp.name), efselab)
    yield Text(filepath=Path(temp.name).joinpath("10-sv.txt"))


@pytest.fixture(scope="function", name="restore_en_tag_text_instance")
def restore_en_tag_text_instance_fixture(temp):
    restore("tagged", resources_path.joinpath("10-en.tag"), Path(temp.name), udpipe)
    yield Text(filepath=Path(temp.name).joinpath("10-en.txt"))


@pytest.fixture(scope="function", name="restore_sv_norm_text_instance")
def restore_sv_spell_text_instance_fixture(temp):
    restore("normalized", resources_path.joinpath("10-sv.spell"), Path(temp.name), efselab)
    yield Text(filepath=Path(temp.name).joinpath("10-sv.txt"))


@pytest.fixture(scope="function", name="restore_en_norm_text_instance")
def restore_en_spell_text_instance_fixture(temp):
    restore("normalized", resources_path.joinpath("10-en.spell"), Path(temp.name), udpipe)
    yield Text(filepath=Path(temp.name).joinpath("10-en.txt"))


@pytest.fixture(scope="function", name="restore_sv_norm_tag_text_instance")
def restore_sv_norm_tag_text_instance_fixture(temp):
    restore("normalized", resources_path.joinpath(sv_norm_tag), Path(temp.name), efselab)
    restore("tagged", resources_path.joinpath(sv_norm_tag), Path(temp.name), efselab)
    yield Text(filepath=Path(temp.name).joinpath("10-sv-norm.txt"))


@pytest.fixture(scope="function", name="restore_en_norm_tag_text_instance")
def restore_en_norm_tag_text_instance_fixture(temp):
    restore("normalized", resources_path.joinpath(en_norm_tag), Path(temp.name), udpipe)
    restore("tagged", resources_path.joinpath(en_norm_tag), Path(temp.name), udpipe)
    yield Text(filepath=Path(temp.name).joinpath("10-en-norm.txt"))


######################################################
#      Test cases: annotate from annotated text      #
######################################################
def test_update_from_tokenized_to_parse_efselab(restore_sv_tok_text_instance, sv_conll_md5):    
    run(restore_sv_tok_text_instance, "parsed", efselab)
    text_postprocess(restore_sv_tok_text_instance, efselab)
    assert sv_conll_md5 == get_md5(restore_sv_tok_text_instance.conll)


def test_update_from_tokenzied_to_parse_udpipe(restore_en_tok_text_instance, en_conll_md5):
    run(restore_en_tok_text_instance, "parsed", udpipe)
    text_postprocess(restore_en_tok_text_instance, udpipe)
    assert en_conll_md5 == get_md5_without_comments(restore_en_tok_text_instance.conll)


def test_update_from_tagged_to_parse_efselab(restore_sv_tag_text_instance, sv_conll_md5):
    run(restore_sv_tag_text_instance, "parsed", efselab)
    text_postprocess(restore_sv_tag_text_instance, efselab)
    assert sv_conll_md5 == get_md5(restore_sv_tag_text_instance.conll)


def test_update_from_tagged_to_parse_udpipe(restore_en_tag_text_instance, en_conll_md5):
    run(restore_en_tag_text_instance, "parsed", udpipe)
    text_postprocess(restore_en_tag_text_instance, udpipe)
    assert en_conll_md5 == get_md5_without_comments(restore_en_tag_text_instance.conll)


def test_update_from_tokenized_to_tag_efselab(restore_sv_tok_text_instance, sv_tag_md5):
    run(restore_sv_tok_text_instance, "tagged", efselab)
    text_postprocess(restore_sv_tok_text_instance, efselab)
    assert sv_tag_md5 == get_md5(restore_sv_tok_text_instance.conll)


def test_update_from_tokenized_to_tag_udpipe(restore_en_tok_text_instance, en_tag_md5):
    run(restore_en_tok_text_instance, "tagged", udpipe)
    text_postprocess(restore_en_tok_text_instance, udpipe)
    assert en_tag_md5 == get_md5_without_comments(restore_en_tok_text_instance.conll)


######################################################
# Test cases: annotate from normalized annotated text#
######################################################
def test_update_from_normalized_to_parse_efselab(restore_sv_norm_text_instance, sv_conll_norm_md5):
    run(restore_sv_norm_text_instance, "parsed", efselab)
    text_postprocess(restore_sv_norm_text_instance, efselab)
    assert sv_conll_norm_md5 == get_md5(restore_sv_norm_text_instance.conll)


def test_update_from_normalized_to_parse_udpipe(restore_en_norm_text_instance, en_conll_norm_md5):
    run(restore_en_norm_text_instance, "parsed", udpipe)
    text_postprocess(restore_en_norm_text_instance, udpipe)
    assert en_conll_norm_md5 == get_md5_without_comments(restore_en_norm_text_instance.conll)


def test_update_from_normalized_to_tag_efselab(restore_sv_norm_text_instance, sv_tag_norm_md5):
    run(restore_sv_norm_text_instance, "tagged", efselab)
    text_postprocess(restore_sv_norm_text_instance, efselab)
    assert sv_tag_norm_md5 == get_md5(restore_sv_norm_text_instance.conll)


def test_update_from_normalized_to_tag_udpipe(restore_en_norm_text_instance, en_tag_norm_md5):
    run(restore_en_norm_text_instance, "tagged", udpipe)
    text_postprocess(restore_en_norm_text_instance, udpipe)
    assert en_tag_norm_md5 == get_md5_without_comments(restore_en_norm_text_instance.conll)


def test_update_from_normalized_tagged_to_parse_efselab(restore_sv_norm_tag_text_instance, sv_conll_norm_md5):
    run(restore_sv_norm_tag_text_instance, "parsed", efselab)
    text_postprocess(restore_sv_norm_tag_text_instance, efselab)
    assert sv_conll_norm_md5 == get_md5(restore_sv_norm_tag_text_instance.conll)


# def test_update_from_normalized_tagged_to_parse_udpipe(restore_en_norm_tag_text_instance, en_conll_norm_md5):
#     run(restore_en_norm_tag_text_instance, "parsed", udpipe)
#     text_postprocess(restore_en_norm_tag_text_instance, udpipe)
#     assert en_conll_norm_md5 == get_md5_without_comments(restore_en_norm_tag_text_instance.conll)


def test_update_from_normalized_tagged_to_parse_udpipe(restore_en_norm_tag_text_instance, en_conll_norm_md5):
    annotate(restore_en_norm_tag_text_instance, "tagged", "parsed", udpipe)
    assert en_conll_norm_md5 == get_md5_without_comments(restore_en_norm_tag_text_instance.conll)