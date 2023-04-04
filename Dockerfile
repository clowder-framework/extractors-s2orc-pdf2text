FROM python:3-alpine3.12

RUN apk --update add python3 py3-pip && rm -rf /var/lib/apt/lists/*

COPY doc2json ./doc2json
COPY tests ./tests
COPY build_run.sh setup.py requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

WORKDIR ./
ENV PYTHONPATH=./

EXPOSE 8070

#CMD ["bash", "build_run.sh"]
CMD ["python3","doc2json/grobid2json/process_pdf.py", "-i", "tests/pdf/N18-3011.pdf", "-t", "temp_dir/", "-o", "output_dir/"]
