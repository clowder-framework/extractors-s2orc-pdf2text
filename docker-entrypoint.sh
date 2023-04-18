#!/usr/bin/env bash

GrobidHome="$HOME/grobid-0.6.1/"

if [ $1 = "textextractor" ]; then
  ./setup_run_grobid.sh
  python3 textextractor.py
else
  exec "$@"
fi


