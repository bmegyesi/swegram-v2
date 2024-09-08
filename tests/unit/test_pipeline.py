
from unittest import TestCase
from unittest import mock

from swegram_main.pipeline import pipeline


@mock.patch("swegram_main.pipeline.pipeline.tokenize_")
def test_tokenize(mock_tokenize):
    mock_tokenizer = "mock_tokenizer"
    mock_text = mock.Mock()
    pipeline.tokenzie()
    ...

