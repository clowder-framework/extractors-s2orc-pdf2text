# Convert json to csv

import json
import logging

import pandas as pd
from doc2txt.sentence_segmentation import split_text_unit

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
    # RCTCheck fix: Read the UTF-8 JSON consistently across operating systems.
    json_file = open(json_input_file, encoding='utf-8')
    json_data = json.load(json_file)  # load json object to a dictionary

    title_text = json_data["title"]["text"]
    title_coords = json_data["title"]["coords"]
    pdf_json_data = json_data["pdf_parse"]
    abstract_data = pdf_json_data["abstract"]
    body_data = pdf_json_data["body_text"]
    back_matter_data = pdf_json_data["back_matter"]

    # convert to dataframe
    title_data = [input_filename, 'title', title_text, title_coords]
    title_df = pd.DataFrame([title_data], columns=['file', 'section', 'sentence', 'coordinates'])
    # Get the text and section from the body
    abstract_df = extract_sentences(input_filename, abstract_data)
    body_df = extract_sentences(input_filename, body_data)
    back_matter_df = extract_sentences(input_filename, back_matter_data)

    # RCTCheck fix: Captions/notes live in ref_entries, outside the original
    # abstract/body/back-matter export. Include them with explicit section labels.
    caption_data = []
    note_data = []
    for reference_id, entry in pdf_json_data.get('ref_entries', {}).items():
        reference_type = entry.get('type_str', entry.get('type'))
        if reference_type not in {'figure', 'table'}:
            continue
        sentences = entry.get('sentences')
        # RCTCheck fix: Support older JSON with caption text but no sentence list.
        # Mark legacy caption text for the same sentence splitting used for TEI.
        if not sentences and entry.get('text'):
            sentences = [{'sentence': entry['text'], 'coords': None,
                          'provenance': {'segmentation': 'unsegmented_text',
                                         'tei_element': 'legacy_caption'}}]
        caption_data.append({
            'section': reference_type.capitalize() + ' caption',
            'text': sentences or []
        })
        note_data.append({
            'section': reference_type.capitalize() + ' note',
            'text': entry.get('notes') or []
        })
    caption_df = extract_sentences(input_filename, caption_data)
    note_df = extract_sentences(input_filename, note_data)
    # RCTCheck fix: Keep existing records in order and append captions/notes.
    # Retain the four-column CSV contract; extra provenance remains in JSON.
    frames = [title_df, abstract_df, body_df, back_matter_df, caption_df, note_df]
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
    # sometimes the data is an empty list []
    if not data:
        return pd.DataFrame(columns=['file', 'section', 'sentence', 'coordinates'])
    list_df = []
    for para in data:
        for i, s in enumerate(para['text']):
            # Handle both dictionary and string formats
            if isinstance(s, dict):
                # RCTCheck fix: Also support JSON produced by the earlier
                # retention-only patch. Tagged GROBID/derived units are unchanged.
                units = split_text_unit(s)
            elif isinstance(s, str):
                units = split_text_unit({'sentence': s, 'coords': None,
                                         'provenance': {'segmentation': 'unsegmented_text',
                                                        'tei_element': 'legacy_text'}})
            else:
                # Skip unexpected formats
                continue
                
            for unit in units:
                new_row = {'file': input_file, 'section': para['section'],
                           'sentence': unit.get('sentence', ''),
                           'coordinates': unit.get('coords', '')}
                list_df.append(new_row)
    df = pd.DataFrame(list_df)

    return df if len(list_df) > 0 else pd.DataFrame(columns=['file', 'section', 'sentence', 'coordinates'])
