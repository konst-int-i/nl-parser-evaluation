import subprocess
from box import Box
from src.utils import *
from typing import *

def treeview(config: Box) -> None:
    """
    Pipeline wrapper to run treeview for a given parser


    Returns:
        None
    """
    parser = config.treeview

    evaluate_all_samples(config, parser)

    return None



def evaluate_all_samples(config: Box, parser: str):
    """
    Function launches the treeviewer for all samples but sample 22.
    Sample 22 cannot be evaluated since all parsers conduct faulty sentence
    boundary detection, meaning that they treat the second sentence in sample 22
    as a seperate sentence, while the index count should continue due to cross-sentence
    dependencies.


    Args:
        config: main project config
        parser: parser for evaluation

    Returns:
        None, but launches the MaltEval TreeViewer
    """
    valid_parsers = config.parse_files.to_dict().keys()
    assert parser in valid_parsers, f"Invalid parser, select one of {valid_parser}"

    parse_file = Path(config.parse_path).joinpath(config.parse_files[parser])
    gs_path = Path(config.gold_path).joinpath(config.files.gold_conll)

    # remove last two sentences due to sentence boundary inconsistency (does not work in MatlEval otherwise)
    eval_file_final  =  _remove_last_two_sents(parse_file)
    gs_file_final = _remove_last_two_sents(gs_path)

    # Run MaltEval on all but last sentence
    bash_command = f"java -jar malteval_dist_20141005/lib/MaltEval.jar " \
                   f"-s {eval_file_final} " \
                   f"-g {gs_file_final} -v 1"

    output, error = run_bash(bash_command)

    return None


def evaluate_single_sample(config: Box, parser: str, sample_no: int) -> None:
    """
    Launch tree viewer for a given parser and sample number
    Args:
        parser (str): parser to evaluate against the gold standard
        smaple_no (int): sample to evaluate

    Returns:
        None
    """

    valid_parsers = config.parse_files.to_dict().keys()
    assert parser in valid_parsers, f"Invdalid parser, select one of {valid_parser}"

    assert sample_no in SAMPLES, f"Invalid sample number selected. Valid numbers; {SAMPLES}"

    sample_path = Path(config.parse_path).joinpath(config.parse_files[parser]).parent
    if parser in ["nn", "pcfg"]:
        filename = f"sample_{sample_no}.txt.conll"
    else:
        filename = f"sample_{sample_no}.conll"
    sample_path = sample_path.joinpath(filename)

    gs_path = Path(config.gold_path).joinpath(f"sample_{sample_no}.conll")

    bash_command = f"java -jar malteval_dist_20141005/lib/MaltEval.jar " \
               f"-s {sample_path} " \
               f"-g {gs_path} -v 1"

    output, error = run_bash(bash_command)


    return None

def _remove_last_two_sents(filepath: Union[str, Path]) -> None:

    with open(filepath, "r") as f:
        parsed = f.read()

    split_parsed = parsed.split("\n\n")
    parsed_removed = split_parsed[:11]
    parsed_removed = "\n\n".join(parsed_removed)

    # save as new up file in directory
    updated_file = filepath.parts[-1].split(".")
    updated_file[0] += "_eval"
    updated_file = ".".join(updated_file)
    write_path = filepath.parent.joinpath(updated_file)

    with open(write_path, "w") as f:
        f.write(parsed_removed)

    return write_path


if __name__ == "__main__":
    config = read_config("config.yml")

    # evaluate_single_sample(config, "pcfg", 1)

    evaluate_all_samples(config, "malt")