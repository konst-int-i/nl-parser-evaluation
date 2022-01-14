from pathlib import Path
import time
import yaml
from box import Box
import logging
import subprocess

# global variables
SAMPLES = [1, 2, 5, 7, 10, 17, 19, 20, 21, 22]

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s][%(filename)s][%(module)s.%(funcName)s:%(lineno)d] %(message)s",
    handlers=[logging.StreamHandler()],
)


def read_config(path: Path) -> Box:
    """

    Args:
        path: path to config file
    Returns:
        Box: box object containing the read ``config.yml``

    """
    with open(Path(path), "r") as f:
        config = yaml.safe_load(f)

    # return config
    return Box(config)


# -*- coding: utf-8 -*-
import sys
import logging
from box import Box
from typing import *

# logger = logging.getLogger(__name__)


def run_bash(command: str) -> Tuple[str, str]:
    """
    Wrapper function to run a Bash command from Python using the ``subprocess`` library

    Args:
        command (str): bash command to execute

    Returns:
        Tuple[str, str]: output and error stream of the bash executable as a tuple
    """
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return output, error


def import_object_by_name(name: str) -> ClassVar:
    """
    Import by name and return imported module/function/class
    Args:
        name (str): module/function/class to import, e.g. 'pandas.read_csv'
            will return read_csv function as
            defined by pandas
    Returns:
        imported object
    """
    class_name = name.split(".")[-1]
    module_name = ".".join(name.split(".")[:-1])
    print(module_name)

    if module_name == "":
        return getattr(sys.modules[__name__], class_name)

    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)


def run_pipeline(config: Box) -> None:
    """
    Wrapper class which reads the pipeline steps from the
    ``pipeline.yml`` and executes them in order
    Args:
        config (Box): main config
    Returns:
        None
    """
    logging.info("STARTING PIPELINE RUN")
    logging.info("STEPS: ")
    for step in config.pipeline:
        logging.info(f"- {step}")

    num_steps = len(config.pipeline)
    for idx, name in enumerate(config.pipeline):
        logging.info(f"PIPELINE STEP {idx+1}/{num_steps}: {name}")
        import_object_by_name(name)(config)


class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise ValueError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise ValueError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return elapsed_time
