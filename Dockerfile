FROM python:3.10

COPY setup.py requirements.txt ./

# install some libgcc requirements
RUN apt-get install -y libxml2 libxslt-dev
RUN pip install -r requirements.txt --no-cache-dir

COPY doc2txt ./doc2txt
COPY pdf2text.py ./
COPY extractor_info.json ./

EXPOSE 8070

CMD ["python3","pdf2text.py", "--heartbeat", "40"]
