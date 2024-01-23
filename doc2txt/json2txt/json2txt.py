# Convert json to text

import json
import logging

# create log object with current module name
log = logging.getLogger(__name__)


def process_json(input_file):
    """
    Method to convert json file to text.
    Extracts data from specific json fields and return a list of strings as text
    Args:
        input_file (str): Json input file
    Returns:
        output (list): List of text data extracted from json
    """
    json_file = open(input_file)
    json_data = json.load(json_file)  # load json object to a dictionary
    # if using grobid, one can use the pdf_parse key and title key.
    title_text = json_data["title"]
    pdf_json_data = json_data["pdf_parse"]
    abstract_data = pdf_json_data["abstract"]
    body_data = pdf_json_data["body_text"]
    output = []
    sections = set()

    output.append(title_text)
    # Get the text and section from the body
    abstract_text_list, abstract_section_list = extract_text_and_section(abstract_data)
    body_text_list, body_section_list = extract_text_and_section(body_data)

    for i, (text,section) in enumerate(zip(abstract_text_list, abstract_section_list)):
        if text:
            if section not in sections:
                output.append(section)  # add section header if not present in the output
                sections.add(section)
            output.append(text)

    for i, (text,section) in enumerate(zip(body_text_list, body_section_list)):
        if text:
            if section not in sections:
                output.append(section)
                sections.add(section)
            output.append(text)

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
                # yield from item_generator(v, lookup_key)
                # no nested lookups. only text in the first dictionary items is appended to output
                pass
    elif isinstance(json_data, list):
        for item in json_data:
            yield from item_generator(item, lookup_key)


def extract_text_and_section(data):
    """
    Method to extract text and section from the body
    Args:
        data (dict): Json input data
    Returns:
        texts (list): List of text data extracted from json
        sections (list): List of section data extracted from json
    """
    # Remove character spans from 'text' field
    for item in data:
        spans = item['cite_spans'] + item['ref_spans']
        spans.sort(key=lambda x: x['start'], reverse=True)  # Sort in reverse order to avoid messing up the indices
        for span in spans:
            item['text'] = item['text'][:span['start']] + item['text'][span['end']:]

    texts = [item["text"] for item in data]
    sections = [item["section"] for item in data]
    return texts, sections
