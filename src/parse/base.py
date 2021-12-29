import pandas as pd
from typing import *
from abc import abstractmethod
from box import Box
import stanza
from src.utils import *
from pathlib import Path
from stanza.utils.conll import CoNLL
import os


class BaseParse(object):
    """
    Base class defining the structure of all parsers used in this project
    """

    def __init__(self, config: Box):
        self.config = config

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    def _post_process(self) -> None:
        pass


class Malt(BaseParse):
    def __init__(self, config):
        super().__init__(config)
        self.preprocess()

    def run(self):
        """
        Wrapper function running preprocessing, parsing and post-processing
        """
        self.preprocess()
        self.parse()
        self.postprocess()

    def parse(self):

        os.chdir("maltparser-1.9.2")

        bash_command = """
        for i in 1 2 5 7 10 17 19 20 21 22
        do
            java -Xmx1024m -jar maltparser-1.9.2.jar -if conllx -c engmalt.linear-1.7.mco -i ../data/raw/sample_${i}.conll -o ../data/parses/malt/sample_${i}.conll -m parse -a nivreeager -l libsvm
        done
        """
        subprocess.check_output(bash_command, shell=True)

        os.chdir("../")

    def preprocess(self) -> None:
        stanford_preprocessing = stanza.Pipeline(lang="en", processors="tokenize,pos")

        for i in SAMPLES:
            with open(
                Path(self.config.data_path).joinpath(f"sample_{i}.txt"), "r"
            ) as f:
                sample = f.read()
                doc = stanford_preprocessing(sample)
            conll_text = CoNLL.doc2conll_text(doc)
            # strip trailing whitespace/newlines
            conll_text = conll_text.rstrip()

            with open(
                Path(self.config.data_path).joinpath(f"sample_{i}.conll"), "w"
            ) as f:
                f.write(conll_text)

        return None

    def postprocess(self) -> None:
        # concatenate MALT samples
        all_samples = ""
        for i in SAMPLES:
            with open(f"data/parses/malt/sample_{i}.conll", "r") as f:
                sample = f.read()
            all_samples += sample

        with open(f"data/parses/malt/selected_samples.conll", "w") as f:
            f.write(all_samples)


if __name__ == "__main__":
    config = read_config("config.yml")
    malt = Malt(config)
    malt.run()
