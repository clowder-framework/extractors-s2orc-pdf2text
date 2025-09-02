# Convert scientific papers to TEXT and JSON

This Clowder extractor converts pdf documents to text and json.
It uses GROBID 0.8.0 to convert pdf to xml and then uses s2orc-doc2json to convert xml to json. The doc2txt/json2txt is used to convert json to text.

This project is a part of [S2ORC](https://github.com/allenai/s2orc). For S2ORC, we convert PDFs to JSON using Grobid and a custom TEI.XML to JSON parser. That TEI.XML to JSON parser (`grobid2json`) is made available here. We additionally process LaTeX dumps from arXiv. That parser (`tex2json`) is also made available here.

The S2ORC github page includes a JSON schema, but it may be easier to understand that schema based on the python classes in `doc2json/s2orc.py`.

This custom JSON schema is also used for the [CORD-19](https://github.com/allenai/cord19) project, so those who have interacted with CORD-19 may find this format familiar.

For more info on Clowder extractors, read this [documentation](https://clowder-framework.readthedocs.io/en/latest/develop/extractors.html).
For more info on GROBID read this [documentation](https://grobid.readthedocs.io/en/latest/Introduction/#:~:text=GROBID%20is%20a%20machine%20learning,made%20available%20in%20open%20source.).

## Run pdf2text-extractor in local using python
Run grobid/grobid:0.8.0 docker image from docker desktop.

**Caveat:** grobid:0.8.0 is not supported by Mac M1 chip. If using Mac silicon, switch to grobid:0.6.2

```
(rctenv) NCSA-P10E69253:extractors-s2orc-pdf2text minum$ pwd
/Users/minum/Documents/NCSA/Clowder/Clowder_Github/extractors-s2orc-pdf2text
```

in `doc2txt/grobid2json/grobid/grobid_client.py` : change "grobid_server": "0.0.0.0",
`python -m doc2txt.grobid2json.process_pdf -i tests/pdf/N18-3011.pdf -t temp_dir/ -o output_dir/`

### Process a PDF

There are a couple of test PDFs in `tests/input/` if you'd like to try with that.

1. Using docker :
- Run docker build :  ` docker build . -t extractors-pdf2text:0.1`. Then `docker run extractors-pdf2text:0.1`.
- Using docker-compose : `docker-compose up`

2. Using python console :

```console
python doc2json/grobid2json/process_pdf.py -i tests/pdf/N18-3011.pdf -t temp_dir/ -o output_dir/
```

This will generate a JSON file in the specified `output_dir`. If unspecified, the file will be in the `output/` directory from your path.

- The extractor will generate a `tei.xml`, `json` and `csv` file.
- The main process is `process_pdf_file()` method.
- Grobid is used to generate the `tei.xml` file which has all the details. The process is `client.process_pdf(input_file, input_filename, temp_dir, "processFulltextDocument")`
- S2ORC package convets the `tei.xml` file to `json` . The process is `paper = convert_tei_xml_file_to_s2orc_json(tei_file)`
- We convert the json file to csv file in the format required for RCT model inference. The process is `output_df = process_json2csv(input_filename, json_file)`


## Setup your environment

NOTE: Conda is shown but any other python env manager should be fine

Go [here](https://docs.conda.io/en/latest/miniconda.html) to install the latest version of miniconda.

Then, create an environment:

```console
conda create -n doc2json python=3.8 pytest
conda activate doc2json
pip install -r requirements.txt
python setup.py develop
```

## PDF Processing

The current `grobid2json` tool uses Grobid to first process each PDF into XML, then extracts paper components from the XML.

### Install Grobid

You will need to have Java installed on your machine. Then, you can install your own version of Grobid and get it running.

1. Using docker (recommended) : 
1.1 With grobid:0.6.2 -
```
docker pull grobid/grobid:0.6.2

docker run -p 8070:8070 grobid/grobid:0.6.2
```

1.2 With grobid:0.8.0 - 
```
docker pull grobid/grobid:0.8.0

docker run -p 8070:8070 grobid/grobid:0.8.0
```
The above comman

2. OR Using script:

```console
bash build_run.sh
```

Note: before running this script, make sure the paths match your installation path. Else it will fail to install.

This will setup, install and run Grobid, currently hard-coded as version 0.6.1. Don't worry if it gets stuck at 87%; this is normal and means Grobid is ready to process PDFs.

The expected port for the Grobid service is 8070, but you can change this as well. Make sure to edit the port in both the Grobid config file as well as `grobid/grobid_client.py` and `docker-compose.yml`.

For more information on S2ORC-DOC2JSON refer https://github.com/allenai/s2orc-doc2json

On a successful `docker run` command, grobid service will get started and in terminal you should be able to see [these logs are per this screenshot](./grobid-docker-run.png)


### Citation
If you use this utility in your research, please cite:

```bibtex
@inproceedings{lo-wang-2020-s2orc,
    title = "{S}2{ORC}: The Semantic Scholar Open Research Corpus",
    author = "Lo, Kyle  and Wang, Lucy Lu  and Neumann, Mark  and Kinney, Rodney  and Weld, Daniel",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-main.447",
    doi = "10.18653/v1/2020.acl-main.447",
    pages = "4969--4983"
}
```

# Use as a Clowder Extractor

Clowder extractor for converting pdf documents to xml, json and csv format.

## Build extractor image

- Run `docker build . -t hub.ncsa.illinois.edu/clowder/extractors-pdf2text:<version>` to build docker image
- If you ran into error `[Errno 28] No space left on device:`, try below:
    - Free more spaces by running `docker system prune --all` 
    - Increase the Disk image size. You can find the configuration in Docker Desktop

## Publish Image to Private NCSA repo
- Login first: `docker login hub.ncsa.illinois.edu`
- Run `docker image push hub.ncsa.illinois.edu/clowder/extractors-pdf2text:<version>`

## Deployment
- Please refer to Clowder instructions
