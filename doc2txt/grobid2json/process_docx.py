# Python module to convert docx to txt file

import os
import json
import argparse
import time
import logging
from docx_utils.flatten import opc_to_flat_opc

from doc2txt.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json, convert_tei_xml_soup_to_s2orc_json
from doc2txt.json2txt.json2txt import process_json

# create log object with current module name
log = logging.getLogger(__name__)

BASE_TEMP_DIR = 'temp'
BASE_OUTPUT_DIR = 'output'

def process_docx_file(
        input_file: str,
        input_filename :str,
        temp_dir: str,
        output_dir: str
) -> [str, str, str]:
    """
     Process Office Open XML (docx) file and get JSON representation. Extract the text from the JSON representation and write to a txt file
    :param input_file: input file resource
    :param input_filename: input filename resource
    :param temp_dir: temporary directory path to store tei xml file
    :param output_dir: output directory path to store output json and txt files
    :return: xml file, json output file, txt output file
    """

    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # filenames for tei and json outputs
    tei_xml_file = os.path.join(temp_dir, f'{input_filename}.tei.xml')
    json_file = os.path.join(output_dir, f'{input_filename}.json')
    txt_file = os.path.join(output_dir, f'{input_filename}.txt')

    # check if input file exists and output file doesn't
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} doesn't exist")
    if os.path.exists(json_file):
        log.warning(f'{json_file} already exists!')

    opc_to_flat_opc(input_file, tei_xml_file)
    paper = convert_tei_xml_file_to_s2orc_json(tei_xml_file)

    # write to file
    with open(json_file, 'w') as outf:
        json.dump(paper.release_json(), outf, indent=4, sort_keys=False)

    # extract text field from json and write to file
    output_txt = process_json(json_file, "text")
    with open(txt_file, 'w') as outfile:
        for text in output_txt:
            outfile.write(f"{text}\n")

    return tei_xml_file, json_file, txt_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run S2ORC PDF2JSON")
    parser.add_argument("-i", "--input", default=None, help="path to the input PDF file")
    parser.add_argument("-t", "--temp", default=BASE_TEMP_DIR, help="path to the temp dir for putting tei xml files")
    parser.add_argument("-o", "--output", default=BASE_OUTPUT_DIR, help="path to the output dir for putting json and txt files")
    parser.add_argument("-k", "--keep", action='store_true')

    args = parser.parse_args()

    input_path = args.input
    temp_path = args.temp
    output_path = args.output
    keep_temp = args.keep

    start_time = time.time()

    os.makedirs(temp_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    input_filename = os.path.splitext(os.path.basename(input_path))[0]
    tei_xml_file, json_file, txt_file = process_docx_file(input_path, input_filename, temp_path, output_path)

    runtime = round(time.time() - start_time, 3)
    print("runtime: %s seconds " % (runtime))
    print('done.')
