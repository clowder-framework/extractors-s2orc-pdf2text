#!/usr/bin/env bash

if [ $1 = "extractor" ]; then
  ./setup_run_grobid.sh &
  Grobid_PID=$!
  # check if grobid service is running. get the second line output of gradlew status and check if busy
  while [[ $(./gradlew --status | sed -n '2 p' | grep "BUSY") ]]
  do
    # gradle is installed. run gradle
    echo $(./gradlew --status)
    # check if grobid is running
    response=$(curl http://grobid:8070/api/version)
    if [[ "$response" == "200" ]]; then
      echo "python"
      python3 textextractor.py --heartbeat 40
    fi
  done
else
  exec "$@"
fi

# wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

