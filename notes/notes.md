## Steps to generate cloze questions

- input: word list (e.g., a sublist of AWL)
- preprocess: collect the derivatives of each word using ChatGPT
- retrieve the pos of the words
- retrieve the inflexives of all words
- generate a sentence from each word with the given pos and inflexives
  - length
- create a blank at the keyword
- find 3 distractors
	- with the same pos and inflexive with the keyword
- test if the distractor fit in the sentence with ChatGPT
	- "does it make sense (grammarly correct and sentimantically appropriate), answer only yes or no"


## Inflection

- [bjascob/LemmInflect: A python module for English lemmatization and inflection.](https://github.com/bjascob/LemmInflect)
- (NOT GOOD) [pyinflect](https://pypi.org/project/pyinflect/)
  - the words in this library is not enough, missing records like "available", "data"