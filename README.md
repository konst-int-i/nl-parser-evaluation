
# Transition-Based and Probabilistic Parsing of Grammatical Relations

This repository was used for an experimental evaluation of three natural language parsing systems:

- **Stanford Probabilistic Context Free Grammar (PCFG) Parser**: unlexicalized PCFG using maximum-likelihood estimates 
from the Penn treebank for its rule probabilities and the CKY algorithm to select the best parse from the parse forest
- **MALT arc-eager parser**: system for data-driven dependency-only parsing which implements 9 different deterministic 
parsing algorithms and 2 machine learning packages. We use the `nivreeager` parsing algorithm alongside the 
`libsvm` learning algorithm for the transition predictions and its default features
- **Stanford Neural Dependency Parser**: Also a transition-based parser, but improves on the MALT parser by a) using a 
different transition system, b) using embedding-based feature representations, c) using a neural network
with cube activation function instead of an SVM as a classifier

## Installation

To run the code, please download the following parsers: 
- [Stanford Core NLP library](https://stanfordnlp.github.io/CoreNLP/) release 4.3.2 - save the extracted folder in the 
root of this repository. This contains both the NN and PCFG parser
- [MALT Parser](http://www.maltparser.org/) version - also save in repository root
- [MaltEval](http://www.maltparser.org/malteval.html) - evaluation tool for dependency parsers

## Run instructions

The code is separated into multiple pipeline steps, which can be configured in the `config.yml`.

 - `src.parse_malt`: Runs the MALT parser on the gold standard sentences and saves the parsed output in `data/parses/malt`
 - `src.parse_pcfg`: Runs the PCFG parser on the gold standard sentences and saves the parsed output in `data/parses/pcfg/conllu`
 - `src.parse_nn`: Runs the PCFG parser on the gold standard sentences and saves the parsed output in `data/parses/pcfg/conllu`
 - `src.gold_standard`: Reads in the `data/gold_standard` and converts it to CoNLL-U format
 - `src.eval`: Evaluates all parsers by dependency relation type and relation length
 - `src.treeview`: Launches `MaltEval TreeViewer` (see example below)

On first execution, it's important that all pipeline steps are run. Following this, you can toggle the desired pipeline 
steps on and off to only run a subset. After first execution, each pipeline step will run independent of the others.  

## Example

After executing the full pipeline, you can review the output of each parser using the `TreeViewer`. To select which 
parser to view set the `treeview` flat in the `config.yml`. 

[!img](treeviewer_example.png)

