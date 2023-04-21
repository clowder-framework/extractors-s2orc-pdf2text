FROM python:3.10

COPY doc2txt ./doc2txt
COPY tests ./tests
COPY build_run.sh setup.py textextractor.py requirements.txt extractor_info.json ./

# install some libgcc requirements
RUN apt-get install -y libxml2 libxslt-dev

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

CMD ["python3","textextractor.py", "--heartbeat", "40"]
