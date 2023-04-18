FROM python:3.10

COPY doc2json ./doc2json
COPY tests ./tests
COPY scripts/setup_run_grobid.sh ./setup_run_grobid.sh
COPY docker-entrypoint.sh textextractor.py requirements.txt extractor_info.json ./
COPY docker-entrypoint.sh /usr/local/bin/

# install some libgcc requirements
RUN apt-get install -y libxml2 libxslt-dev

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

RUN ["chmod", "+x", "docker-entrypoint.sh"]
RUN ["chmod", "+x", "setup_run_grobid.sh"]
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["textextractor"]
#CMD ["python3","textextractor.py", "--heartbeat", "40"]
