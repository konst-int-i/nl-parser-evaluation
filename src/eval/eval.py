"""
Runs MaltEval program by calling its Java API
"""

import subprocess
import numpy as np
import pandas as pd
from box import Box
import logging
from src import *
from pathlib import Path

def evaluate_single_parser(config: Box, parser: str) -> str:
    """
    Takes in single parser and runs MaltEval to generate evaluation metrics
    (precision, recall, f1) by dependency relation type of given parser compared
    to the gold standard

    Args:
        parser (str): parser under evaluation. Valid args: ["nn", "malt", "pcfg"]

    Returns:
        str: MaltEval output as a string shwoing the precision, recal and f1-score by
            dependency relation type
    """
    parse_files = config.parse_files.to_dict()
    valid_args = list(parse_files.keys())
    assert parser in valid_args, f"Invalid parser name. Choose one of {valid_args}"
    logging.info(f"Evaluating {parser.upper()} parser")

    parse_path = Path(config.parse_path).joinpath(parse_files[parser])
    gold_path = Path(config.gold_path).joinpath(config.files.gold_conll)

    bash_command = f"java -jar malteval_dist_20141005/lib/MaltEval.jar " \
                   f"--Metric self " \
                   f"--GroupBy Deprel " \
                   f"-s {parse_path} " \
                   f"-g {gold_path}"

    logging.info(f"Executing: {bash_command}")

    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # convert bytes object to regular string
    output_str = output.decode("utf-8")

    logging.info(output_str)

    return output_str

def malt_to_df(output: str) -> pd.DataFrame:
    """
    Function which takes in the MaltEval output string and converts it to a
    pandas dataframe

    Args:
        output (str): MaltEval output string - returned from ``evaluate_single_parser``
            method

    Returns:
        pd.DataFrame: dataframe with parse performance by dependency relation type
    """

    parse_eval = output.rstrip().split("\n")

    eval_cols = ["precision", "recall", "fscore", "Deprel"]
    eval_df = pd.DataFrame(columns=eval_cols)
    for deprel in parse_eval[12:]:
        entries = deprel.split(" ")
        entries = [e for e in entries if e != ""]
        eval_df = eval_df.append(pd.Series(entries, index=eval_cols), ignore_index=True)

        # post-processing
    eval_df = eval_df.replace("-", np.nan)
    eval_df = eval_df.astype(
        {"precision": "float",
         "recall": "float",
         "fscore": "float"}
    )

    return eval_df



def evaluate_all_parsers(config: Box) -> None:
    """
    Function which
    Args:
        config (Box): project config

    Returns:

    """
    parser_dfs = []
    for parser in config.eval:
        df = malt_to_df(evaluate_single_parser(config, parser))
        parser_dfs.append(df)


    # pcfg_df = malt_to_df(evaluate_single_parser(config, "pcfg"))
    # nn_df = malt_to_df(evaluate_single_parser(config, "nn"))
    # malt_df = malt_to_df(evaluate_single_parser(config, "malt"))
    # print(config.eval.to_list())

    eval_df = pd.concat(parser_dfs, keys=config.eval.to_list(), axis=1).swaplevel(0, 1,axis=1).sort_index(level=0, axis=1)
    # eval_df = pd.concat([pcfg_df, malt_df, nn_df], keys=["pcfg", "malt", "nn"], axis=1).swaplevel(0, 1,axis=1).sort_index(level=0, axis=1)

    return eval_df


def eval(config):
    """
    Wrapper function for pipeline
    """

    evaluate_all_parsers(config)


if __name__ == "__main__":
    config = read_config("config.yml")

    eval_df = evaluate_all_parsers(config)

    print(eval_df)