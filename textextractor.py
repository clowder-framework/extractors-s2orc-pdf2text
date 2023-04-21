# text extractor wrapper
# wraps process_pdf.py

import time
import logging
import json
import os

from pyclowder.extractors import Extractor
import pyclowder.files

from doc2txt.grobid2json.process_pdf import process_pdf_file
#from doc2txt.grobid2json.grobid.grobid_client import GrobidClient
#from doc2txt.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json


# create log object with current module name
log = logging.getLogger(__name__)

BASE_TEMP_DIR = 'temp'
BASE_OUTPUT_DIR = 'output'
BASE_LOG_DIR = 'log'


class TextExtractor(Extractor):
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
        # {'type': 'file', 'id': '6435b226e4b02b1506038ec5', 'intermediate_id': '6435b226e4b02b1506038ec5', 'name': 'N18-3011.pdf', 'file_ext': '.pdf', 'parent': {'type': 'dataset', 'id': '64344255e4b0a99d8062e6e0'}, 'local_paths': ['/tmp/tmp2hw6l5ra.pdf']}
        #log.info(resource)

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
        output_xml_file, output_json_file = process_pdf_file(input_file, input_filename, temp_dir, output_dir)
        log.info("Output files : %s, %s", output_xml_file, output_json_file)

        runtime = round(time.time() - start_time, 3)
        log.info("runtime: %s seconds " % runtime)
        connector.message_process(resource, "Pdf to text conversion finished.")

        # clean existing duplicate
        files_in_dataset = pyclowder.datasets.get_file_list(connector, host, secret_key, dataset_id)
        for file in files_in_dataset:
            if file["filename"] == output_json_file or file["filename"] == output_xml_file:
                url = '%sapi/files/%s?key=%s' % (host, file["id"], secret_key)
                connector.delete(url, verify=connector.ssl_verify if connector else True)
        connector.message_process(resource, "Check for duplicate files...")

        # upload to clowder
        pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_json_file)
        pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_xml_file)
        connector.message_process(resource, "Uploading output files to Clowder...")


if __name__ == "__main__":
    # # for testing
    #process_pdf_file("tests/pdf/N18-3011.pdf", BASE_TEMP_DIR, BASE_OUTPUT_DIR)

    extractor = TextExtractor()
    extractor.start()