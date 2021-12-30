from abc import abstractmethod
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

    @abstractmethod
    def _post_process(self) -> None:
        pass

    def _fix_sentence_split(self, conllu_path: Union[Path, str]) -> None:
        """
        Quickfix to avoid splitting last quotation mark. Since the NN parser assigns a new index to the sentence
        spanning the quote, we assign the preceding sentence ending as the head.

        Note that this post-processing is required to evaluate the file using MaltParse
        Args:
            conllu_path (str): path to full parsed samples in conll-u format

        Returns:
            None
        """
        logging.info(f"Fixing apostrophe parse error in file: {conllu_path}")

        with open(conllu_path, "r") as f:
            conll = f.read()
        # temporarily split string
        conll_split = conll.split("\n")

        # take last element and split
        last_elem = conll_split[-1].split("\t")
        last_elem[0] = "11"
        last_elem[6] = "10"
        last_elem[7] = "punct"
        last_elem = "\t".join(last_elem)

        # remove space
        conll_split.pop(-2)
        conll_split[-1] = last_elem
        conll_fixed = "\n".join(conll_split)

        with open(conllu_path, "w") as f:
            f.write(conll_fixed)

        return None

    def _conll_to_conllu(self, conll_path: str) -> None:
        """
        Function which takes in the original sentence and path to the CoNLL file
        generated by the Stanford CoreNLP module (for PCFG parse) and converts it
        to the CoNLLU format.

        Note that this is using the following positional mapping of the two CoNLL files (0-indexed):
            - 0 --> 0
            - 1 --> 1
            - 2 --> 2
            - 3 --> 4
            - 4 --> 8
            - 5 --> 6
            - 6 --> 7

        All other places (3, 5) are filled with "_". The 10th (startchar/endchar) is derived
        using the raw string


        """
        # with open(Path(self.config.data_path).joinpath(self.config.files.raw_samples), "r") as f:
        #     sentence = f.read()
        with open(conll_path, "r") as f:
            conll = f.read().split("\n")

        # conll_split
        cs = [token.split("\t") for token in conll]

        conllu_str = ""

        for w in cs:
            # handle extra newlines (to ensure sentence boundaries are transferred)
            if len(w) == 1:
                conllu_str += "\n"
                continue

            # replace "ROOT" with "root" (for consistency with other format)
            if w[6] == "ROOT":
                w[6] = "root"

            conllu_line = (
                f"{w[0]}\t{w[1]}\t{w[2]}\t_\t{w[3]}\t_\t{w[5]}\t{w[6]}\t{w[4]}\t_\n"
            )
            conllu_str += conllu_line

        # strip trailing whitespace
        conllu_str = conllu_str.rstrip()

        # write to file
        target_file = Path(conll_path).name
        # Note that the file extension still needs to be .conll for malteval to recognize the files from the directory
        target_path = Path(conll_path).parents[1].joinpath(f"conllu/{target_file}")
        with open(target_path, "w") as f:
            f.write(conllu_str)


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


class PCFG(BaseParse):
    def __int__(self, config):
        super().__init__(config)

    def run(self):
        self.parse()
        self.postprocess("data/parses/pcfg/conll/selected_samples.txt.conll")

    def parse(self):

        os.chdir("stanford-corenlp-4.3.2")
        bash_command = """
        java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props ../pcfg-parse.props -file ../data/raw/selected_samples.txt
        """
        subprocess.check_output(bash_command, shell=True)

        os.chdir("../")

    def postprocess(self, conll_path) -> None:
        self._conll_to_conllu(conll_path)
        super()._fix_sentence_split(
            "data/parses/pcfg/conllu/selected_samples.txt.conll"
        )


class StanfordNN(BaseParse):
    def __init__(self, config):
        super().__init__(config)

    def run(self):
        self.parse()

        self.postprocess("data/parses/nn/conll/selected_samples.txt.conll")

    def parse(self):
        os.chdir("stanford-corenlp-4.3.2")

        bash_command = """
        java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props ../nn-parse.props -file ../data/raw/selected_samples.txt
        """
        subprocess.check_output(bash_command, shell=True)

        os.chdir("../")

    def postprocess(self, conll_path: str) -> None:

        self._conll_to_conllu(conll_path)
        super()._fix_sentence_split("data/parses/nn/conllu/selected_samples.txt.conll")


if __name__ == "__main__":
    config = read_config("config.yml")
    malt = Malt(config)
    malt.run()
