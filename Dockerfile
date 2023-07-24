FROM python:3.10

COPY doc2txt ./doc2txt

# install some libgcc requirements
RUN apt-get install -y libxml2 libxslt-dev

RUN pip install -r requirements.txt --no-cache-dir

COPY setup.py pdf2text.py requirements.txt extractor_info.json ./

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

CMD ["python3","pdf2text.py", "--heartbeat", "40"]
