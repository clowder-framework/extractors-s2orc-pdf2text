FROM python:3-alpine3.12

RUN apk --update add python3 py3-pip && rm -rf /var/lib/apt/lists/*

COPY doc2json ./doc2json
COPY tests ./tests
COPY build_run.sh setup.py textextractor.py requirements.txt extractor_info.json ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# install pyclowder
#RUN python -m pip install --ignore-installed pyclowder

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

#CMD ["bash", "build_run.sh"]
CMD ["python3","textextractor.py", "--heartbeat", "40"]
