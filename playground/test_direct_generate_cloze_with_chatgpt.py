from chatgpt_wrapper import ChatGPT

DEBUG = True


grammer_tempalte = 'grammar mistake "Anyway, this report shows Mori’s useful work properly. "'

FIXED_RESULT_CLOZE = """Which of the following options completes the sentence "The measurement was ________" ?

A) inaccurate
B) untimely
C) approximate
D) accurate


The correct answer is "D) accurate"."""

class MyBotWrapper:
    def __init__(self) -> None:
        self.bot = ChatGPT()
        pass

    def create_cloze(self, keyword):
        response = self.ask_for_cloze(keyword=keyword)
        result = self.parse_cloze_response(keyword=keyword, response=response)
        return result
    
    def ask_for_cloze(self, keyword):
        if DEBUG:
            return FIXED_RESULT_CLOZE
        question = self.compose_question(keyword)
        response = self.bot.ask(question)
        return response


    def compose_question(self, keyword):
        template = 'create a filling in the blank multi choice question with "{keyword}" as the correct answer'
        question = template.format(keyword="accurate")
        return question
    
    def parse_cloze_response(self, keyword, response):
        """parse the response from OpenGPT, return a dict containing 
        {'keyword', 'stem', 'distractor 1', 'distractor 2', 'distractor 3' }

        Args:
            response (_type_): _description_
        """
        blocks = [x.strip() for x in response.split("\n\n")]
        len(blocks)
        
        stem = blocks[0]
        option_block = blocks[1]
        options = [raw.split(' ')[1] for raw in option_block.split('\n')]
        if keyword in options:
            options.remove(keyword)
        
        res = {
            'stem': stem,
            'keyword': keyword,
            'distractor 1': options[0],
            'distractor 2': options[1],
            'distractor 3': options[2],
        }
        
        return res

class DataProcessor:
    """A class that process a data file(.csv, .xls, etc.) and process each line and then output to a file
    """
    def read_file(path):
        pass
    def run(self):
        pass

def main():
    
    keyword = "accurate"
    bot = MyBotWrapper()
    response = bot.create_cloze(keyword)
    print(response)  # prints the response from chatGPT


if __name__ == '__main__':
    main()
