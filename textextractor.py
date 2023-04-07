# text extractor wrapper
# wraps process_pdf.py

import time
import logging
import os
from pyclowder.extractors import Extractor
import pyclowder.files

from doc2json.grobid2json.process_pdf import process_pdf_file

BASE_TEMP_DIR = '/'
BASE_OUTPUT_DIR = '/'
BASE_LOG_DIR = '/log'

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
        # print(resource)

        logger = logging.getLogger(__name__)
        input_file = resource["local_paths"][0]
        input_file_id = resource['id']
        dataset_id = resource['parent'].get('id')

        temp_dir = BASE_TEMP_DIR
        output_dir = BASE_OUTPUT_DIR
        # get paper id as the name of the file
        paper_id = '.'.join(input_file.split('/')[-1].split('.')[:-1])
        tei_file = os.path.join(temp_dir, f'{paper_id}.tei.xml')
        output_file = os.path.join(output_dir, f'{paper_id}.json')

        # These process messages will appear in the Clowder UI under Extractions.
        connector.message_process(resource, "Loading contents of file...")

        # process pdf file
        start_time = time.time()
        input_filename = resource["name"]
        process_pdf_file(input_file, temp_dir, output_dir)
        runtime = round(time.time() - start_time, 3)
        print("runtime: %s seconds " % runtime)
        print('done.')
        connector.message_process(resource, "Pdf to text conversion finished...")

        # clean existing duplicate
        files_in_dataset = pyclowder.datasets.get_file_list(connector, host, secret_key, dataset_id)
        for file in files_in_dataset:
            if file["filename"] == output_file:
                url = '%sapi/files/%s?key=%s' % (host, file["id"], secret_key)
                connector.delete(url, verify=connector.ssl_verify if connector else True)
        connector.message_process(resource, "Check for duplicate...")

        # upload to clowder
        pyclowder.files.upload_to_dataset(connector, host, secret_key, dataset_id, output_file)
        connector.message_process(resource, "Upload processed file to Clowder...")


if __name__ == "__main__":
    # # for testing
    #process_pdf_file("tests/pdf/N18-3011.pdf", BASE_TEMP_DIR, BASE_OUTPUT_DIR)

    extractor = TextExtractor()
    extractor.start()