import json
import requests
from pprint import pprint

def parse_json_data(json_data, headword=None):
    result_list = []
    # Extract 'fl' (function label) and 'sense' information
    if isinstance(json_data, list):  # Check if the response is a list (word found)
        for entry in json_data:
            fl = entry.get('fl')
            senses = entry.get('def', [])

            # print(f'Function Label: {fl}')
            id = entry.get('meta', {}).get('id')
            current_headword = id.split(':')[0]
            if headword is not None and current_headword != headword:
                continue
            result_entry = {'id': id, 'fl': fl, 'senses': []}

            for sense in senses:
                for sseq in sense.get('sseq', []):
                    for item in sseq:
                        if isinstance(item, list) and item[0] == 'sense':
                            sn = item[1].get('sn')
                            dt = item[1].get('dt', [])
                            sense_text = []
                            # print(f'\tSense {sn}:')
                            for text_type, text_content in dt:
                                if text_type == 'text':
                                    # print(f'\t\t{text_content}')
                                    sense_text.append(text_content)
                            result_entry['senses'].append({'sn': sn, 'text': sense_text})
            result_list.append(result_entry)
    else:
        print(f'No results found for the keyword: {keyword}')    
    
    return result_list


def fetch_dictionary_data(api_key, keyword):
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any errors in the HTTP response

        # Parse the JSON response
        json_data = response.json()
        return parse_json_data(json_data, keyword)
    except requests.exceptions.RequestException as e:
        print(f'Error making API request: {e}')


def parse_file():
    with open('./playground/word.json', 'r') as f:
        json_data = json.load(f)
        return parse_json_data(json_data)
        

if __name__ == '__main__':
    # Replace 'your-api-key' with your actual Merriam-Webster API key
    api_key = '91d6f2de-f9c1-45bf-8feb-f778f875ec42'
    keyword = 'formula'  # Replace with the word you want to look up

    result = fetch_dictionary_data(api_key, keyword)
    # result = parse_file()
    pprint(result)