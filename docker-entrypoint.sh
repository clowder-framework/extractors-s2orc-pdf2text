#!/usr/bin/env bash

GrobidHome="$HOME/grobid-0.6.1/"

if [ $1 = "python3" ]; then
  ./setup_run_grobid.sh
  exec "$@"
else
  exec "$@"
fi


