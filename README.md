
# nl-parser-evaluation


Repository used for Natural Language and Syntax Parsing Practical

## Installation

To run the code, please download the following two packages: 
- [Stanford Core NLP library](https://stanfordnlp.github.io/CoreNLP/) release 4.3.2 - save the extracted folder in the 
root of this repository.
- [Shift-reduce parser](https://nlp.stanford.edu/software/stanford-srparser-2014-10-23-models.jar) version - 
save the downloaded models in the `stanford-corenlp-4.3.2` directory (from 
the instruction above).

## Parsers

This assignment is comparing the following parsers: 
- Stanford Neural Network Dependency Parser

The parses produce use version 4.3.2 of the Stanford SR parsers available at 
https://nlp.stanford.edu/software/lex-parser.html. 

### Stanford NN Parser

To run the samples generated by the Stanford SR parses, please run the following from the `stanford-corenlp-4.3.2`
directory:

```
java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props ../nn-dependencies.props
```

Note that the configurations for the CoreNLP pipeline are specified in 
`nn-dependencies.props`. View [here](https://stanfordnlp.github.io/CoreNLP/pipeline.html) 
for a full list of available props. The file `data/parse/nn-dependencies/selected_samples.txt.output` contains the 
directed dependencies from the parse.

### RASP parser

1. Download the `rasp3os` directory
2. Move the directory to the root of this repository
3. Run: `./rasp3os/scripts/rasp.sh -m < data/raw/selected_samples.txt > data/parses/rasp/rasp_parse.txt`
from the repository root
4. Outputs directed dependencies

### PCFG parser

Outputs constituency parse tree

```
java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props ../pcfg-parse.props
```

### Other


