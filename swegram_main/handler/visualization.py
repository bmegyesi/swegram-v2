import os
from copy import copy
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional, Dict, Union
from swegram_main.data.features import Feature
from swegram_main.data.texts import Corpus
from swegram_main.handler.handler import load


class Visualization:

    def __init__(
        self, input_path: Path, language: str, output_dir: Optional[Path],
        include_tags: Optional[List[str]],
        exclude_tags: Optional[List[str]]
    ) -> None:
        self.input_path = input_path
        self.corpus: Corpus = load(input_path, language, include_tags, exclude_tags)
        self.outdir = output_dir or Path(os.getcwd())
            

    def filter(
        self, units: List[str], aspects: List[str],
        include_features: List[str], exclude_features: List[str],
        pprint: bool = False, save_as: str = "txt"
    ) -> None:
        self.pprint = pprint
        self.aspects = aspects
        self.save_as = save_as
        data = OrderedDict()
        if "corpus" in units:
            data["corpus"] = self.filter_instance(self.corpus, include_features, exclude_features)
        if "text" in units:
            data["text"] = [
                self.filter_instance(text, include_features, exclude_features) for text in self.corpus.texts
            ]
        if "paragraph" in units:
            data["paragraph"] = [
                [
                    self.filter_instance(p, include_features, exclude_features)
                    for p in text.paragraphs
                ]
                for text in self.corpus.texts
            ]
        if "sentence" in units:
            data["sentence"] = [
                [
                    [
                        self.filter_instance(s, include_features, exclude_features)
                        for s in p.sentences
                    ] for p in text.paragraphs
                ] for text in self.corpus.texts
            ]
        self.outfile_name = self.outdir.joinpath(f"statistic-{self.input_path.with_suffix(f'.{save_as}').name}")
        if save_as == "txt" or pprint:
            self.save(data)

    def append_in_text(self, content: str) -> None:
        with open(self.outfile_name, "a+") as output_file:
            output_file.write(f"{content}\n")

    def filter_instance(
        self, instance, include_features: List[str], exclude_features: List[str]
    ) -> List[Dict[str, Dict[str, Union[int, float]]]]:
        return [self.filter_aspect(instance, aspect, include_features, exclude_features) for aspect in self.aspects]

    def filter_aspect(self, instance, aspect: str, include_features: List[str], exclude_features: List[str]):
        aspect_dict = copy(getattr(instance, aspect))
        if exclude_features:
            for feature in exclude_features:
                if feature in aspect_dict:
                    del aspect_dict[feature]
        if include_features:
            for feature in aspect_dict:
                if feature not in include_features:
                    del aspect_dict[feature]
        return aspect_dict

    def save(self, data: OrderedDict) -> None:
        for unit in data:
            if unit == "corpus":
                self.save_instance(None, unit, data[unit])
            elif unit == "text":
                for text_index, text_instance in enumerate(data[unit], 1):
                    self.save_instance(str(text_index), unit, text_instance)
            elif unit == "paragraph":
                for ti, text_list in enumerate(data[unit], 1):
                    for pi, paragraph_instance in enumerate(text_list, 1):
                        self.save_instance(f"{ti}-{pi}", unit, paragraph_instance)
            elif unit == "sentence":
                for ti, text_list in enumerate(data[unit], 1):
                    for pi, p_list in enumerate(text_list, 1):
                        for si, sentence_instance in enumerate(p_list, 1):
                            self.save_instance(f"{ti}-{pi}-{si}", unit, sentence_instance)
            if self.pprint:
                print()

    def save_instance(self, index: Optional[str], unit: str, aspect_instances: List[OrderedDict]) -> None:
        for aspect_name, instance in zip(self.aspects, aspect_instances):
            self.save_title(unit, aspect_name, index)
            for fn, f in instance.items():
                self.save_feature(fn, f)
            if self.pprint:
                print()
        if self.pprint:
            print()
        if self.save_as == "txt":
            self.append_in_text("")

    def save_title(self, unit: str, aspect_name: str, index: Optional[str]) -> None:
        title = f"{' ':>2}{'-'.join([e for e in [unit.title(), index, aspect_name] if e]):>40}" \
                f"{'|':>4}{'-'*13}|{'-'*13}|{'-'*13}|"
        if self.pprint:
            print(title)
        if self.save_as == "txt":
            self.append_in_text(title)

    def save_feature(self, fn: str, f: Feature) -> None:
        c = lambda v: v or ""
        feature = f"{' ':>2}{fn:>40}{'|':>4}{c(f.scalar):>10}{'|':>4}{c(f.mean):>10}{'|':>4}{c(f.median):>10}{'|':>4}"
        if self.pprint:
            print(feature)
        if self.save_as == "txt":
            self.append_in_text(feature)
