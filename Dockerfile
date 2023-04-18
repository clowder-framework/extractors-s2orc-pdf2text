FROM python:3.10

# install some libgcc requirements
RUN apt-get install -y libxml2 libxslt-dev

COPY --from=openjdk:18-slim / /

# install openJDK11
# RUN apt-get install -y default-jdk
# RUN apt-get update && apt-get install -y ant && apt-get clean;

# fix certificate issues
# RUN apt-get install ca-certificates-java && apt-get clean && update-ca-certificates -f;

# setup JAVA_HOME
#ENV JAVA_HOME /usr/local/openjdk-18/
#ENV PATH $JAVA_HOME/bin:$PATH
# RUN export JAVA_HOME


COPY doc2json ./doc2json
COPY tests ./tests
COPY scripts/setup_run_grobid.sh ./setup_run_grobid.sh
COPY docker-entrypoint.sh textextractor.py requirements.txt extractor_info.json ./
COPY docker-entrypoint.sh /usr/local/bin/

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

RUN ["chmod", "+x", "docker-entrypoint.sh"]
RUN ["chmod", "+x", "setup_run_grobid.sh"]
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["extractor"]
#CMD ["python3","textextractor.py", "--heartbeat", "40"]
