# DEBUG = True
DEBUG = False

DEFAULT_LOG_LEVEL = "INFO"
# DEFAULT_LOG_LEVEL = "DEBUG"

OFFLINE_CHATGPT = True
OFFLINE_CHATGPT = False

DEFAULT_MODEL = 'gpt-3.5-turbo-0301'
DEFAULT_MODEL = 'gpt-3.5-turbo'
# DEFAULT_MODEL = 'gpt-4'


SUBLIST = 3
DOMAIN = 'General Academic'
LEVEL_START = 'B1'
LEVEL_END = 'lower B2'
# The number of times to retry when ChatGPT fails to generate a sentence for a word
RETRY_COUNT_FOR_SINGLE_WORD = 2

# The start position of keyword selection
KEYWORD_START_POS = 0

# The number of keywords for generating sentences, -1 means all
KEYWORD_COUNT = -1
# KEYWORD_COUNT = 5

TEST_DISTRACTOR_COUNT = 10 # The number of distractors to ask ChatGPT to test rationality in one trial
DISTRACTOR_COUNT = 3 # The number of distractors to output to result

# Fix the randomness, -1 means random
#   seems not working
RANDOM_SEED = 42
# RANDOM_SEED = -1

