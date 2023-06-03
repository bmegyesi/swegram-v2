import os


data = [[(size, lang) for size in [10 ** i for i in range(1, 6)]] for lang in ['en', 'sv']]
en_corpus = "europarl-v7.sv-en.en"
sv_corpus = "europarl-v7.sv-en.sv"


class GenerateFileNameError(Exception):
    """generate file name eror"""


def size2name(size: int):
    if size // 10 ** 6:
        return f"{size // 10 ** 6}m"
    if size // 10 ** 3:
        return f"{size // 10 ** 3}k"
    return size


def get_file_name(size: int, language: str):
    if language.lower() in ['en', 'english']:
        ext = 'en'
    elif language.lower() in ['sv', 'swedish']:
        ext = 'sv'
    else:
        raise GenerateFileNameError('The language is not recoginzed. Supported languages are English and Swedish')
    return f"{size2name(size)}-{ext}.txt"


def initialize_test_texts():
    for test_setting, language_path in zip(data, [en_corpus, sv_corpus]):
        with open(os.path.join('sv-en', language_path), 'r') as corpus:
            for size, language in test_setting:
                with open(get_file_name(size, language), 'w') as output_file:
                    while size:
                        output_file.write(corpus.readline())
                        size -= 1


if __name__ == '__main__':
    initialize_test_texts()
