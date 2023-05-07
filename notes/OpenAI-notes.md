## Examples

[Playground](https://beta.openai.com/playground/p/default-grammar?mode=complete&model=text-davinci-003)

``` txt
Create 3 sentences with "accurate":

1. The company wants to ensure their financial records are kept accurate.
2. The accurate measurement of the object's size is important in the experiment.
3. She checked the facts three times to ensure the reporting was accurate.
```

```
Mask the word "accurate" in three sentences of no less than 15 words

1. She was able to give a very __accurate__ estimate on how much the items cost.
2. The results from the experiment were __accurate__ to within two decimal places.
3. The survey responses were carefully analyzed to ensure the data was __accurate__.
```


```
Mask the word "accurate" in three sentences that contain at least two clauses.

1. The results of the experiment were surprisingly ********, given the complexity of the task.
2. The ******** measurements taken by the team allowed them to draw meaningful conclusions.
3. The team was confident that their ******** calculations would lead to a successful outcome.
```


```
find words that satisfy two conditions:
1. semantically related to "accurate" based on word embeddings
2. with high perplexity when filled in the blank "The company wants to ensure their financial records are kept __"


precise, meticulous, exact, thorough, meticulousness
```



```py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "Given the context,"

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="rank the following list of words in descending order in terms of their perplexity measures when placed into the sentence \"The results of the experiment were surprisingly ********, given the complexity of the task.\"\n1. accurate\n2. surprising\n3. astonishing\n4. unexpected\n the descending order of perplexity measures would be: astonishing, surprising, unexpected, accurate.",
  temperature=0,
  max_tokens=60,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
```

### ChatGPT

[Playground](https://chat.openai.com/chat)

```
rank the following list of words in descending order in terms of their perplexity measures when placed into the sentence "The results of the experiment were surprisingly ********, given the complexity of the task."
1. accurate
2. surprising
3. astonishing

---
Based on the context provided, the ranking of the words in descending order of perplexity would be:

astonishing
surprising
accurate
The word "astonishing" would be the most perplexing or unexpected word to use in the sentence, followed by "surprising," and then "accurate," which may be seen as the least surprising or unexpected word to use in the context provided.
```