import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree


def main():
    input_file = "data/output/2024-01-25_23-27-05-AWL_sublist1-cloze.xlsx"
    output_file = input_file.replace(".xlsx", ".xml")

    df = pd.read_excel(input_file)

    # Convert DataFrame to XML
    xml_tree = dataframe_to_xml(df)

    write_xml_to_file(xml_tree, output_file)

    print(f"XML file saved to {output_file}")


def create_question_xml(question_data):
    question = Element("question", type="multichoice")

    name = SubElement(question, "name")
    text_name = SubElement(name, "text")
    text_name.text = question_data["Correct Answer"]

    question_text = SubElement(question, "questiontext", format="plain_text")
    text_question = SubElement(question_text, "text")
    text_question.text = question_data["Sentence"]

    single = SubElement(question, "single")
    single.text = "true"
    shuffle_answers = SubElement(question, "shuffleanswers")
    shuffle_answers.text = "true"
    answer_numbering = SubElement(question, "answernumbering")
    answer_numbering.text = "abc"

    answer_options = ["Correct Answer", "Distractor 1", "Distractor 2", "Distractor 3"]
    for option in answer_options:
        answer_fraction = (
            "100" if question_data[option] == question_data["Correct Answer"] else "0"
        )
        answer = SubElement(
            question, "answer", fraction=answer_fraction, format="plain_text"
        )
        text_answer = SubElement(answer, "text")
        text_answer.text = question_data[option]

    return question


def dataframe_to_xml(dataframe, nrows=None):
    quiz = Element("quiz")

    for index, row in dataframe.iterrows():
        if nrows is not None and index >= nrows:
            break
        question_xml = create_question_xml(row)
        quiz.append(question_xml)

    return quiz


def write_xml_to_file(xml_tree, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(tostring(xml_tree, encoding="utf-8").decode())


if __name__ == "__main__":
    main()
