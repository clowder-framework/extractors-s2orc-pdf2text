#!/usr/bin/env bash

if [ $1 = "extractor" ]; then
  ./setup_run_grobid.sh &
  python3 textextractor.py --heartbeat 40
else
  exec "$@"
fi

# wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

