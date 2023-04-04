# Convert scientific papers to TEXT and JSON

This Clowder extractor converts pdf documents to text and json.
It uses Grobid 0.6.2 

This project is a part of [S2ORC](https://github.com/allenai/s2orc). For S2ORC, we convert PDFs to JSON using Grobid and a custom TEI.XML to JSON parser. That TEI.XML to JSON parser (`grobid2json`) is made available here. We additionally process LaTeX dumps from arXiv. That parser (`tex2json`) is also made available here.

The S2ORC github page includes a JSON schema, but it may be easier to understand that schema based on the python classes in `doc2json/s2orc.py`.

This custom JSON schema is also used for the [CORD-19](https://github.com/allenai/cord19) project, so those who have interacted with CORD-19 may find this format familiar.


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

1. Using docker : 
```
docker pull grobid/grobid:0.6.2

docker run -p 8070:8070 grobid/grobid:0.6.2
```

2. OR Using script:

```console
bash build_run.sh
```

Note: before running this script, make sure the paths match your installation path. Else it will fail to install.

This will setup, install and run Grobid, currently hard-coded as version 0.6.1. Don't worry if it gets stuck at 87%; this is normal and means Grobid is ready to process PDFs.

The expected port for the Grobid service is 8070, but you can change this as well. Make sure to edit the port in both the Grobid config file as well as `grobid/grobid_client.py` and `docker-compose.yml`.

### Process a PDF

There are a couple of test PDFs in `tests/input/` if you'd like to try with that.

1. Using docker :
- Run docker build :  ` docker build . -t doc2json:0.1`. Then `docker run doc2json:0.1`.
- Using docker-compose : `docker-compose up`

2. Using python console :

```console
python doc2json/grobid2json/process_pdf.py -i tests/pdf/N18-3011.pdf -t temp_dir/ -o output_dir/
```

This will generate a JSON file in the specified `output_dir`. If unspecified, the file will be in the `output/` directory from your path.

For more information on S2ORC-DOC2JSON refer https://github.com/allenai/s2orc-doc2json

