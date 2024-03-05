# Convert json to csv

import json
import logging

import pandas as pd
from doc2txt.utils.tokenizer import tokenize_sentence

# create log object with current module name
log = logging.getLogger(__name__)


def process_json2csv(input_filename, json_input_file):
    """
    Method to convert json file to text.
    Extracts data from specific json fields and return a list of strings as text
    Args:
        input_filename (str): Input filename
        json_input_file (str): Json input file
    Returns:
        df: pandas dataframe
    """
    log.info("Extracting information from json file: %s", json_input_file)
    json_file = open(json_input_file)
    json_data = json.load(json_file)  # load json object to a dictionary

    title_text = json_data["title"]
    pdf_json_data = json_data["pdf_parse"]
    abstract_data = pdf_json_data["abstract"]
    body_data = pdf_json_data["body_text"]

    # convert to dataframe
    tokenized_title = tokenize_sentence(title_text)
    title_df = pd.DataFrame({'file': input_filename, 'section': 'title', 'sentence': title_text,
                             'prev_sentence': '', 'next_sentence': '',
                             'tokenized_sentence': tokenized_title, 'coordinates': ''})
    # Get the text and section from the body
    abstract_df = extract_sentences(input_filename, abstract_data)
    body_df = extract_sentences(input_filename, body_data)

    frames = [title_df, abstract_df, body_df]
    df = pd.concat(frames)
    # Get the previous sentence
    df['prev_sentence'] = df['sentence'].shift(1)
    # Get the next sentence
    df['next_sentence'] = df['sentence'].shift(-1)

    json_file.close()

    return df

def extract_sentences(input_file, data):
    """
    Method to extract text and section from the body
    Args:
        input_file (str): Json input file
        data (dict): Json input data
    Returns:
        df: pandas dataframe of sentences and related info.
    """
    # [ {text: [ {sentence :str, coords: str} ], cite_spans: List, ref_spans: List, eq_spans: List, section: str}]
    list_df = []
    for para in data:
        for i, s in enumerate(para['text']):
            tokenized_sentence = tokenize_sentence(s['sentence'])
            new_row = {'file': input_file, 'section': para['section'], 'sentence': s['sentence'],
                            'prev_sentence': '', 'next_sentence': '',
                            'tokenized_sentence': tokenized_sentence[0], 'coordinates': s['coords']}
            list_df.append(new_row)
    df = pd.DataFrame(list_df)

    return df if len(list_df) > 0 else pd.DataFrame(columns=['file', 'section', 'sentence', 'prev_sentence', 'next_sentence', 'tokenized_sentence', 'coordinates'])
