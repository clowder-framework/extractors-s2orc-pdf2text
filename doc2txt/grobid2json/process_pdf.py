import os
import json
import argparse
import time
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict

from doc2txt.grobid2json.grobid.grobid_client import GrobidClient
from doc2txt.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json, convert_tei_xml_soup_to_s2orc_json
from doc2txt.json2csv.json2csv import process_json2csv

BASE_TEMP_DIR = 'temp'
BASE_OUTPUT_DIR = 'output'

# create log object with current module name
log = logging.getLogger(__name__)


def process_pdf_stream(input_file: str, sha: str, input_stream: bytes, grobid_config: Optional[Dict] = None) -> Dict:
    """
    Process PDF stream
    :param input_file:
    :param sha:
    :param input_stream:
    :return:
    """
    # process PDF through Grobid -> TEI.XML
    client = GrobidClient(grobid_config)
    tei_text = client.process_pdf_stream(input_file, input_stream, 'temp', "processFulltextDocument")

    # make soup
    soup = BeautifulSoup(tei_text, "xml")

    # get paper
    paper = convert_tei_xml_soup_to_s2orc_json(soup, input_file, sha)

    return paper.release_json('pdf')


def process_pdf_file(
        input_file: str,
        input_filename :str,
        temp_dir: str,
        output_dir: str,
        grobid_config: Optional[Dict] = None
) -> [str, str, str]:
    """
    Process a PDF file and get JSON representation
    :param input_file: input file resource
    :param input_filename: input filename resource
    :param temp_dir:
    :param output_dir:
    :return: xml output file, json output file, csv output file
    """
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # filenames for tei and json outputs
    tei_file = os.path.join(temp_dir, f'{input_filename}.tei.xml')
    json_file = os.path.join(output_dir, f'{input_filename}.json')
    csv_file = os.path.join(output_dir, f'{input_filename}.csv')

    # check if input file exists and output file doesn't
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} doesn't exist")
    if os.path.exists(json_file):
        log.warning(f'{json_file} already exists!')

    # process PDF through Grobid -> TEI.XML
    client = GrobidClient(grobid_config)
    # TODO: compute PDF hash
    # TODO: add grobid version number to output
    client.process_pdf(input_file, input_filename, temp_dir, "processFulltextDocument")

    # process TEI.XML -> JSON
    assert os.path.exists(tei_file)
    paper = convert_tei_xml_file_to_s2orc_json(tei_file)

    # write to file
    with open(json_file, 'w') as outf:
        json.dump(paper.release_json(), outf, indent=4, sort_keys=False)

    # extract fields from json and write to file
    output_df = process_json2csv(input_filename, json_file)
    output_df.to_csv(csv_file, index=False, encoding='utf-8')

    return tei_file, json_file, csv_file


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
    tei_file, json_file, csv_file = process_pdf_file(input_path, input_filename, temp_path, output_path)

    runtime = round(time.time() - start_time, 3)
    print("runtime: %s seconds " % (runtime))
    print('done.')
