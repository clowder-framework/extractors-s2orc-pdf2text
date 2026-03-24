# text extractor wrapper
# wraps process_pdf.py

import time
import logging
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

import requests
from doc2txt.grobid2json.process_pdf import process_pdf_file

# Use api/v2 when CLOWDER_API_VERSION=v2 (Clowder2)
# Also supports CLOWDER_VERSION=2 from clowder2 docker-compose
CLOWDER_API_VERSION = os.environ.get('CLOWDER_API_VERSION') or ('v2' if os.environ.get('CLOWDER_VERSION') == '2' else 'v1')
CLOWDER_API_PATH = 'api/v2' if CLOWDER_API_VERSION == 'v2' else 'api'

from pyclowder.extractors import Extractor
import pyclowder.files

# create log object with current module name
log = logging.getLogger(__name__)

BASE_TEMP_DIR = 'temp'
BASE_OUTPUT_DIR = 'output'
BASE_LOG_DIR = 'log'

def clowder_context_url():
    """JSON-LD context URL for metadata. Override via CLOWDER_CONTEXT_URL env."""
    return os.environ.get(
        'CLOWDER_CONTEXT_URL',
        'http://clowder.ncsa.illinois.edu/contexts/metadata.jsonld'
    )

def clowder_users_url():
    """Clowder users API URL for metadata agent. Override via CLOWDER_USERS_URL env."""
    return os.environ.get(
        'CLOWDER_USERS_URL',
        'http://clowder.ncsa.illinois.edu/api/users'
    )


class Pdf2TextExtractor(Extractor):
    def __init__(self):
        Extractor.__init__(self)

        # add any additional arguments to parser
        # self.parser.add_argument('--max', '-m', type=int, nargs='?', default=-1,
        #                          help='maximum number (default=-1)')

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results
        # uncomment to see the resource
        # log.info(resource)
        # {'type': 'file', 'id': '6435b226e4b02b1506038ec5', 'intermediate_id': '6435b226e4b02b1506038ec5', 'name': 'N18-3011.pdf', 'file_ext': '.pdf', 'parent': {'type': 'dataset', 'id': '64344255e4b0a99d8062e6e0'}, 'local_paths': ['/tmp/tmp2hw6l5ra.pdf']}

        input_file = resource["local_paths"][0]
        input_file_id = resource['id']
        dataset_id = resource['parent'].get('id')
        input_filename = os.path.splitext(os.path.basename(resource["name"]))[0]

        temp_dir = BASE_TEMP_DIR
        output_dir = BASE_OUTPUT_DIR

        # These process messages will appear in the Clowder UI under Extractions.
        connector.message_process(resource, "Loading contents of file...")

        # process pdf file
        start_time = time.time()
        output_xml_file, output_json_file, output_csv_file = process_pdf_file(input_file, input_filename, temp_dir, output_dir)

        log.info("Output files generated : %s, %s, %s", output_xml_file, output_json_file, output_csv_file)
        runtime = round(time.time() - start_time, 3)
        log.info("runtime: %s seconds " % runtime)
        connector.message_process(resource, "Pdf to text conversion finished.")     

        xml_surface_tags = []
        page_width = 600  # default page width and height
        page_height = 800
        # get page height and width from xml file
        if output_xml_file:
            with open(output_xml_file) as f:
                xml = f.read()
                soup = BeautifulSoup(xml, 'xml')
                xml_surface_tags = soup.find_all('surface')
            pass

        if len(xml_surface_tags) > 0:
            log.info("Extracting pdf dimensions from xml file")
            page_width = xml_surface_tags[0]['lrx']
            page_height = xml_surface_tags[0]['lry']

        # clean existing duplicate
        connector.message_process(resource, "Check for duplicate files...")
        files_in_dataset = pyclowder.datasets.get_file_list(connector, host, secret_key, dataset_id)
        for file in files_in_dataset:
            if CLOWDER_API_VERSION == 'v2':
                if file["name"] == output_json_file or file["name"] == output_xml_file:
                    url = '%s%s/files/%s?key=%s' % (host, CLOWDER_API_PATH, file["id"], secret_key)
                    connector.delete(url, verify=connector.ssl_verify if connector else True)
            else:
                if file["filename"] == output_json_file or file["filename"] == output_xml_file:
                    url = '%s%s/files/%s?key=%s' % (host, CLOWDER_API_PATH, file["id"], secret_key)
                    connector.delete(url, verify=connector.ssl_verify if connector else True)

        # upload to clowder
        connector.message_process(resource, "Uploading output files to Clowder...")
        json_fileid = pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_json_file)
        xml_fileid = pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_xml_file)
        csv_fileid = pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_csv_file)
        # upload metadata to dataset
        extracted_files = [
            {"file_id": input_file_id, "filename": input_filename, "description": "Input pdf file"},
            {"file_id": xml_fileid, "filename": output_xml_file, "description": "TEI XML output file from Grobid"},
            {"file_id": json_fileid, "filename": output_json_file, "description": "JSON output file form Grobid"},
            {"file_id": csv_fileid, "filename": output_csv_file, "description": "CSV output file with extracted text, section, and coordinates"}
        ]
        page_dimensions = {"width": page_width, "height": page_height}
        content = {"extractor": "pdf2text-extractor", "extracted_files": extracted_files, "page_dimensions": page_dimensions}
        context = clowder_context_url()
        user_id = clowder_users_url()  # TODO: can update user id in config
        #created_at = datetime.now().strftime("%a %d %B %H:%M:%S UTC %Y")
        agent = {"@type": "user", "user_id": user_id}
        metadata = {"@context": [context], "agent": agent, "content": content}
        pyclowder.datasets.upload_metadata(connector, host, secret_key, dataset_id, metadata)

        # clean up temp_dir and output_dir
        temp_filelist = [f for f in os.listdir(temp_dir)]
        for f in temp_filelist:
            os.remove(os.path.join(temp_dir, f))

        out_filelist = [f for f in os.listdir(output_dir)]
        for f in out_filelist:
            os.remove(os.path.join(output_dir, f))


if __name__ == "__main__":
    # uncomment for testing
    #process_pdf_file("tests/pdf/N18-3011.pdf", "N18-3011", BASE_TEMP_DIR, BASE_OUTPUT_DIR)

    extractor = Pdf2TextExtractor()
    extractor.start()
