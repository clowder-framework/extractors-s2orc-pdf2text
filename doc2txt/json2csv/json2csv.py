# Convert json to csv

import json
import logging

import pandas as pd

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
    title_data = [input_filename, 'title', title_text, '']
    title_df = pd.DataFrame([title_data], columns=['file', 'section', 'sentence', 'coordinates'])
    # Get the text and section from the body
    abstract_df = extract_sentences(input_filename, abstract_data)
    body_df = extract_sentences(input_filename, body_data)

    frames = [title_df, abstract_df, body_df]
    df = pd.concat(frames)

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
            new_row = {'file': input_file, 'section': para['section'],
                       'sentence': s['sentence'], 'coordinates': s['coords']}
            list_df.append(new_row)
    df = pd.DataFrame(list_df)

    return df if len(list_df) > 0 else pd.DataFrame(columns=['file', 'section', 'sentence', 'coordinates'])
