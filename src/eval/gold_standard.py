import csv
import pandas as pd
from box import Box
from src import *
from pathlib import Path
import logging


def gold_standard(config: Box) -> None:
    """
    Wrapper function for pipeline steps
    Function which reads in the gold standard excel file and converts it into
    single file of .conll format with all sentences separated by a newline
    Args:
        config: Box config

    Returns:
        None, but writes file to ``data/gold_standard/gold_standard.conll``
    """

    # Write individual gold standard files
    write_single_file_gs(config)

    # WRITE GOLD STANDARD FOR ALL SENTENCES
    write_full_gs_from_single_files(config)
    return None


def write_single_file_gs(config: Box) -> None:
    """
    Function which reads in Excel file and writes every sample as separate .conll
    file
    Args:
        config (Box): main config

    Returns:
        None, but writes `.conll` files in ``data/gold_standard/`` directory

    """
    # WRITE SAMPLES AS INDIVIDUAL FILES
    logging.info("Writing individual gold standard files")
    gold_path = Path(config.gold_path).joinpath(config.files.gold_excel)
    for idx in SAMPLES:
        sample_name = f"sample_{idx}"
        df = pd.read_excel(gold_path, sheet_name=sample_name, na_filter=True)

        # fix - replace underscores with empty values
        df[["ID", "HEAD"]] = df[["ID", "HEAD"]].replace("_", "")

        write_path = Path(config.gold_path).joinpath(f"sample_{idx}.conll")

        logging.info(f"Writing gold standard files to {write_path}")

        df.to_csv(
            write_path, sep="\t", header=False, index=False, quoting=csv.QUOTE_NONE
        )
    return None


def write_full_gs_from_single_files(config):
    conll_all = ""
    for idx in SAMPLES:
        with open(Path(config.gold_path).joinpath(f"sample_{idx}.conll"), "r") as f:
            sample = f.read()
            conll_all += sample
            conll_all += "\n"

        # remove "tab-only" rows cause by setnence breaks in excel
        conll_split = conll_all.split("\n")
        split_cleaned = []
        for s in conll_split:
            if s == "\t\t\t\t\t\t\t\t\t":
                split_cleaned.append("")
            else:
                split_cleaned.append(s)

        conll_final = ("\n").join(split_cleaned)
    write_path = Path(config.gold_path).joinpath(config.files.gold_conll)
    logging.info(f"Writing full gold standard file to {write_path}")
    with open(write_path, "w") as f:
        f.write(conll_final)


if __name__ == "__main__":
    config = read_config("config.yml")
    gold_standard(config)
