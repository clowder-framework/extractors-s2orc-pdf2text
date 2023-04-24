# Convert json to text

import json
import logging

# create log object with current module name
log = logging.getLogger(__name__)


def process_json(input_file, key):
    """
    Method to convert json file to text.
    Extracts data from the key field and return a list of strings as text
    Args:
        input_file (str): Json input file
        key (str): Json field key to extract data
    Returns:
        output (list): List of text data extracted from json
    """
    json_file = open(input_file)
    json_data = json.load(json_file)  # load json object to a dictionary
    # if using grobid, one can also use the pdf_parse key. uncomment below if needed
    # json_data = json_data["pdf_parse"]
    output = []
    for i in item_generator(json_data, key):
        output.append(i)

    json_file.close()

    return output


def item_generator(json_data, lookup_key):
    """
    Method to extract a field from nested json data.
    Extracts data from the key field and return the value
    Args:
        json_data (str): Json input data
        lookup_key (str): Json field key to extract data
    Returns:
        output (list): List of text data extracted from json
    """
    if isinstance(json_data, dict):
        for k, v in json_data.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_data, list):
        for item in json_data:
            yield from item_generator(item, lookup_key)
