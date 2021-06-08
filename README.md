# Sosweety
This is the code for **[Doing Natural Language Processing in A Natural Way: An NLP toolkit based on object-oriented knowledge base and multi-level grammar base](https://arxiv.org/abs/2105.05227)** 

## Data
Additional data for initialize the knowledge base will be supplied sooner.

## Usage

The system now only can be run in a linux environment with python3.
Right now only Chinese are supported.

1, initialize knowledge base
Execute the three programs in the ./train/1_init_kb directory to initialize the knowledge base. Some initial data are needed, it will be supplied sooner.

Copy the knowledge base file to /dev/shm

2, train with any text corpus.
- 2.1 parse: Parse the corpus into a POS tag file. The default parser is HanLP
- 2.2 analyse: Analyse the parse result to find new knowledge and grammar.
- 2.3 identify: Identify the analyse result manually.
- 2.4 update: Update the knowledge base and grammar base.

There is an example flow in the ./train/general_train_example.