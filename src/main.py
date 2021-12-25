from typing import *
from pathlib import Path
import click
from src import *
import logging
from box import Box
import yaml


def read_samples(config) -> List[str]:
    """
    Reads in text file as list of strings
    Returns:
        List[str]: containing all samples of the input file specified in
            ``config.yml``

    """

    path = Path(f"{config.data_path}{config.input_file}")

    with open(path, "r") as f:
        samples = f.read().split("\n")
    # drop empty strings
    samples = [s for s in samples if s != ""]

    return samples


# implement different tokenizations here
@click.command()
@click.option(
    "--config",
    default="config.yml",
    show_default=True,
    help="Location of the configuration file",
)
def main(config: str) -> None:
    """
    Wrapper function implementing a basic CLI for parser evaluation
    Args:
        config (str): path of the config file - default ``config.yml``

    Returns:
        None
    """

    config = read_config(config)
    run_pipeline(config)
    logging.info("Done executing pipeline")


if __name__ == "__main__":

    main()
    # config = read_config("config.yml")

    # samples = read_samples(config)

    # print(samples)
