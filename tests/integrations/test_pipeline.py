
import hashlib
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from swegram_main.pipeline.pipeline import Pipeline

try:
    workspace = os.environ["SWEGRAM_WORKSPACE"]
except KeyError:
    logging.error("SWEGRAM_WORKSPACE is not setup")
    sys.exit(1)

sv_text = os.path.join(workspace, "tests", "integrations", "10-sv.txt")
en_text = os.path.join(workspace, "tests", "integrations", "10-en.txt")

histnorm_model_sv = "histnorm_sv"
histnorm_model_en = "histnorm_en"
resources_path = Path(f"{workspace}/tests/resources")
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


# ######################################################
# # md5 values for the given target texts (swedish)    #
# ######################################################
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


# ######################################################
@pytest.fixture(scope="function", name="temp")
def temp_fixture():
    yield tempfile.TemporaryDirectory()


@pytest.fixture(scope="function", name="sv")
def sv_fixture():
    yield Path(sv_text)


@pytest.fixture(scope="function", name="sv_pipe")
def sv_pipe_fixture(temp, sv):
    yield Pipeline(sv, output_dir=Path(temp.name), language="sv")


@pytest.fixture(scope="function", name="en")
def en_fixture():
    yield Path(en_text)


@pytest.fixture(scope="function", name="en_pipe")
def en_pipe_fixture(temp, en):
    yield Pipeline(en, output_dir=Path(temp.name), language="en")


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
@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.tokenize
def test_annotation_tokenize_efselab(sv_pipe, sv_conll, sv_tok_md5):
    sv_pipe.run(action="tokenize")
    assert sv_tok_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.tokenize
def test_annotation_tokenize_udpipe(en_pipe, en_conll, en_tok_md5):
    en_pipe.run(action="tokenize")
    assert en_tok_md5 == get_md5_without_comments(en_conll)


@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.normalize
def test_annotation_normalize_efselab(sv_pipe, sv_conll, sv_spell_md5):
    sv_pipe.run(action="normalize")
    assert sv_spell_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.normalize
def test_annotation_normalize_udpipe(en_pipe, en_conll, en_spell_md5):
    en_pipe.run(action="normalize")
    assert en_spell_md5 == get_md5_without_comments(en_conll)


@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.tag
def test_annotation_tag_efselab(sv_pipe, sv_conll, sv_tag_md5):
    sv_pipe.run(action="tag")
    assert sv_tag_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.tag
def test_annotation_tag_udpipe(en_pipe, en_conll, en_tag_md5):
    en_pipe.run(action="tag")
    assert en_tag_md5 == get_md5_without_comments(en_conll)


@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.parse
def test_annotation_parse_efselab(sv_pipe, sv_conll, sv_conll_md5):
    sv_pipe.run(action="parse")
    assert sv_conll_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.parse
def test_annotation_parse_udpipe(en_pipe, en_conll, en_conll_md5):
    en_pipe.run(action="parse")
    assert en_conll_md5 == get_md5_without_comments(en_conll)


@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.normalize
@pytest.mark.tag
def test_annotation_tag_efselab_with_normalization(sv_pipe, sv_conll, sv_tag_norm_md5):
    sv_pipe.normalize()
    sv_pipe.run(action="tag")
    assert sv_tag_norm_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.normalize
@pytest.mark.tag
def test_annotation_tag_udpipe_with_normalization(en_pipe, en_conll, en_tag_norm_md5):
    en_pipe.normalize()
    en_pipe.run(action="tag")
    assert en_tag_norm_md5 == get_md5_without_comments(en_conll)

@pytest.mark.sv
@pytest.mark.annotate
@pytest.mark.normalize
@pytest.mark.parse
def test_annotation_parse_efselab_with_normalization(sv_pipe, sv_conll, sv_conll_norm_md5):
    sv_pipe.normalize()
    sv_pipe.run(action="parse")
    assert sv_conll_norm_md5 == get_md5(sv_conll)


@pytest.mark.en
@pytest.mark.annotate
@pytest.mark.normalize
@pytest.mark.parse
def test_annotation_parse_udpipe_with_normalization(en_pipe, en_conll, en_conll_norm_md5):
    en_pipe.normalize()
    en_pipe.run(action="parse")
    assert en_conll_norm_md5 == get_md5_without_comments(en_conll)


######################################################
#      Fixtures: restore from annotated text         #
######################################################
@pytest.fixture(scope="function", name="sv_tok_path")
def sv_tok_path_fixture(temp):
    sv_tok_path = Path(temp.name).joinpath(sv_tok).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(sv_tok), sv_tok_path)
    yield sv_tok_path


@pytest.fixture(scope="function", name="en_tok_path")
def en_tok_path_fixture(temp):
    en_tok_path = Path(temp.name).joinpath(en_tok).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(en_tok), en_tok_path)
    yield en_tok_path


@pytest.fixture(scope="function", name="sv_tag_path")
def sv_tag_path_fixture(temp):
    sv_tag_path = Path(temp.name).joinpath(sv_tag).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(sv_tok), sv_tag_path)
    yield sv_tag_path


@pytest.fixture(scope="function", name="en_tag_path")
def en_tag_path_fixture(temp):
    en_tag_path = Path(temp.name).joinpath(en_tag).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(en_tag), en_tag_path)
    yield en_tag_path


@pytest.fixture(scope="function", name="sv_norm_path")
def sv_norm_path_fixture(temp):
    sv_norm_path = Path(temp.name).joinpath(sv_spell).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(sv_spell), sv_norm_path)
    yield sv_norm_path


@pytest.fixture(scope="function", name="en_norm_path")
def en_norm_path_fixture(temp):
    en_norm_path = Path(temp.name).joinpath(en_spell).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(en_spell), en_norm_path)
    yield en_norm_path


@pytest.fixture(scope="function", name="sv_tag_norm_path")
def sv_tag_norm_path_fixture(temp):
    sv_tag_norm_path = Path(temp.name).joinpath(sv_norm_tag).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(sv_norm_tag), sv_tag_norm_path)
    yield sv_tag_norm_path


@pytest.fixture(scope="function", name="en_tag_norm_path")
def en_tag_norm_path_fixture(temp):
    en_tag_norm_path = Path(temp.name).joinpath(en_norm_tag).with_suffix(".conll")
    shutil.copy(resources_path.joinpath(en_norm_tag), en_tag_norm_path)
    yield en_tag_norm_path

######################################################
#      Test cases: annotate from annotated text      #
######################################################
@pytest.mark.sv
@pytest.mark.tokenized
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_tokenized_to_parse_efselab(temp, sv_conll_md5, sv_tok_path):
    pipeline = Pipeline(sv_tok_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("parse")
    assert sv_conll_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.tokenized
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_tokenzied_to_parse_udpipe(temp, en_conll_md5, en_tok_path):
    pipeline = Pipeline(en_tok_path, output_dir=Path(temp.name), language="en")
    pipeline.run("parse")
    assert en_conll_md5 == get_md5_without_comments(pipeline.texts[0].conll)


@pytest.mark.sv
@pytest.mark.tagged
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_tagged_to_parse_efselab(temp, sv_conll_md5, sv_tag_path):
    pipeline = Pipeline(sv_tag_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("parse")
    assert sv_conll_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.tagged
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_tagged_to_parse_udpipe(temp, en_conll_md5, en_tag_path):
    pipeline = Pipeline(en_tag_path, output_dir=Path(temp.name), language="en")
    pipeline.run("parse")
    assert en_conll_md5 == get_md5_without_comments(pipeline.texts[0].conll)


@pytest.mark.sv
@pytest.mark.tokenized
@pytest.mark.tag
@pytest.mark.re_annotate
def test_update_from_tokenized_to_tag_efselab(temp, sv_tag_md5, sv_tok_path):
    pipeline = Pipeline(sv_tok_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("tag")
    assert sv_tag_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.tokenized
@pytest.mark.tag
@pytest.mark.re_annotate
def test_update_from_tokenzied_to_tag_udpipe(temp, en_tag_md5, en_tok_path):
    pipeline = Pipeline(en_tok_path, output_dir=Path(temp.name), language="en")
    pipeline.run("tag")
    assert en_tag_md5 == get_md5_without_comments(pipeline.texts[0].conll)


# ######################################################
# # Test cases: annotate from normalized annotated text#
# ######################################################
@pytest.mark.sv
@pytest.mark.normalized
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_normalized_to_parse_efselab(temp, sv_conll_norm_md5, sv_norm_path):
    pipeline = Pipeline(sv_norm_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("parse")
    assert sv_conll_norm_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.normalized
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_normalized_to_parse_udpipe(temp, en_conll_norm_md5, en_norm_path):
    pipeline = Pipeline(en_norm_path, output_dir=Path(temp.name), language="en")
    pipeline.run("parse")
    assert en_conll_norm_md5 == get_md5_without_comments(pipeline.texts[0].conll)


@pytest.mark.sv
@pytest.mark.normalized
@pytest.mark.tag
@pytest.mark.re_annotate
def test_update_from_normalized_to_tag_efselab(temp, sv_tag_norm_md5, sv_norm_path):
    pipeline = Pipeline(sv_norm_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("tag")
    assert sv_tag_norm_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.normalized
@pytest.mark.tag
@pytest.mark.re_annotate
def test_update_from_normalized_to_tag_udpipe(temp, en_tag_norm_md5, en_norm_path):
    pipeline = Pipeline(en_norm_path, output_dir=Path(temp.name), language="en")
    pipeline.run("tag")
    assert en_tag_norm_md5 == get_md5_without_comments(pipeline.texts[0].conll)


@pytest.mark.sv
@pytest.mark.normalized
@pytest.mark.tagged
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_normalized_to_tag_efselab(temp, sv_conll_norm_md5, sv_tag_norm_path):
    pipeline = Pipeline(sv_tag_norm_path, output_dir=Path(temp.name), language="sv")
    pipeline.run("parse")
    assert sv_conll_norm_md5 == get_md5(pipeline.texts[0].conll)


@pytest.mark.en
@pytest.mark.normalized
@pytest.mark.tagged
@pytest.mark.parse
@pytest.mark.re_annotate
def test_update_from_normalized_to_tag_udpipe(temp, en_conll_norm_md5, en_tag_norm_path):
    pipeline = Pipeline(en_tag_norm_path, output_dir=Path(temp.name), language="en")
    pipeline.run("parse")
    assert en_conll_norm_md5 == get_md5_without_comments(pipeline.texts[0].conll)


