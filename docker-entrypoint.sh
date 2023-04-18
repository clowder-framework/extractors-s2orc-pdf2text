#!/usr/bin/env bash

GrobidHome="$HOME/grobid-0.6.1/"

if [ $1 = "extractor" ]; then
  ./setup_run_grobid.sh
  python3 textextractor.py --heartbeat 40
else
  exec "$@"
fi


