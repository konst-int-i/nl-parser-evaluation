"""
File containing pipeline wrappers for parses
"""
from src.parse.base import Malt, StanfordNN, PCFG
from src.utils import *


def parse_nn(config):
    nn = StanfordNN(config)
    nn.run()


def parse_pcfg(config):
    pcfg = PCFG(config)
    pcfg.run()


def parse_malt(config):
    malt = Malt(config)
    malt.run()
