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


def evaluate_single_parser(config: Box, parser: str, groupby: str) -> str:
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

    bash_command = (
        f"java -jar malteval_dist_20141005/lib/MaltEval.jar "
        f"--Metric self "
        f"--GroupBy {groupby} "
        f"-s {parse_path} "
        f"-g {gold_path}"
    )

    logging.info(f"Executing: {bash_command}")

    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # convert bytes object to regular string
    output_str = output.decode("utf-8")

    # logging.debug(output_str)
    logging.info(output_str)

    return output_str


def malt_to_df(output: str, groupby: str = "Deprel") -> pd.DataFrame:
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

    eval_cols = ["precision", "recall", "fscore", groupby]
    eval_df = pd.DataFrame(columns=eval_cols)
    for deprel in parse_eval[12:]:
        entries = deprel.split(" ")
        entries = [e for e in entries if e != ""]
        eval_df = eval_df.append(pd.Series(entries, index=eval_cols), ignore_index=True)

        # post-processing
    eval_df = eval_df.replace("-", np.nan)
    eval_df = eval_df.astype(
        {"precision": "float", "recall": "float", "fscore": "float"}
    )

    return eval_df[[groupby, "precision", "recall", "fscore"]]


def evaluate_all_parsers(config: Box, by: str) -> None:
    """
    Function which
    Args:
        config (Box): project config

    Returns:

    """
    nn_df = malt_to_df(evaluate_single_parser(config, "nn", by), by)
    malt_df = malt_to_df(evaluate_single_parser(config, "malt", by), by)
    pcfg_df = malt_to_df(evaluate_single_parser(config, "pcfg", by), by)

    eval_df = nn_df.merge(
        right=malt_df, how="outer", on=by, validate="1:1", suffixes=["_nn", "_malt"]
    )
    eval_df = eval_df.merge(
        right=pcfg_df, how="outer", on=by, validate="1:1", suffixes=["", "_pcfg"]
    )
    eval_df.rename(
        {
            "precision": "precision_pcfg",
            "recall": "recall_pcfg",
            "fscore": "fscore_pcfg",
        },
        axis=1,
        inplace=True,
    )

    eval_df = eval_df.sort_values(by=by, ascending=True)
    eval_df = eval_df.sort_index(axis=1)

    # drop extremely sparse dependency relations (rows summing to 0)
    eval_df = eval_df.loc[(eval_df.sum(axis=1) != 0), :]

    # add suppport column
    if by == "Deprel":
        dfs = []
        for i in SAMPLES:
            df = pd.read_excel(
                "data/gold_standard/gold_standard.xlsx", sheet_name=f"sample_{i}"
            )
            dfs.append(df)

        gs_df = pd.concat(dfs)
        gs_df = gs_df[["DEPREL"]].dropna().reset_index().drop("index", axis=1)
        support_df = (
            gs_df.value_counts()
            .reset_index()
            .rename({0: "support", "DEPREL": "Deprel"}, axis=1)
        )

        eval_df = eval_df.merge(support_df, on="Deprel", validate="1:1", how="left")

    return eval_df


def eval(config) -> None:
    """
    Wrapper function for pipeline
    """

    deprel_df = evaluate_all_parsers(config, by="Deprel")

    rel_length_df = evaluate_all_parsers(config, by="RelationLength")
    rel_length_df["RelationLength"] = rel_length_df["RelationLength"].astype("int")
    rel_length_df.sort_values(by="RelationLength", inplace=True)

    arc_dir_df = evaluate_all_parsers(config, by="ArcDirection")

    # write to csv
    deprel_path = Path(config.eval_path).joinpath("deprel_eval.csv")
    rel_length_path = Path(config.eval_path).joinpath("arc_length_eval.csv")
    arc_dir_path = Path(config.eval_path).joinpath("arc_dir_eval.csv")

    logging.info(f"Writing parser deprel evaluation to {deprel_path}")
    logging.info(f"Writing parser relation length evaluation to {rel_length_path}")
    logging.info(f"Writing parser arc direction evaluation to {arc_dir_path}")

    deprel_df.to_csv(deprel_path, index=False)
    rel_length_df.to_csv(rel_length_path, index=False)
    arc_dir_df.to_csv(arc_dir_path, index=False)
    return None


if __name__ == "__main__":
    config = read_config("config.yml")

    eval(config)

    # deprel_df = evaluate_all_parsers(config, by="Deprel")
    # rl_df = evaluate_all_parsers(config, by="RelationLength")
    # rl_df["RelationLength"] = rl_df["RelationLength"].astype("int")
    # rl_df.sort_values(by="RelationLength", inplace=True)
    # relation length
    # df = malt_to_df(evaluate_single_parser(config, "nn", "RelationLength"), "RelationLength")
    # print(deprel_df)
    # print(rl_df)

    # print(eval_df)
