#!/usr/bin/env bash

GrobidHome="/grobid-0.6.1/"

if [ $1 = "extractor" ]; then
  cd $GrobidHome
  ./gradlew clean install
  ./gradlew run &
  Grobid_PID=$!
  # check if grobid service is running. get the second line output of gradlew status and check if busy
  while [[ $(./gradlew --status | sed -n '2 p' | grep "BUSY") ]]
  do
    # gradle is installed. run gradle
    echo $(./gradlew --status)
    # check if grobid is running
    response=$(curl http://localhost:8070/api/version)
    if [[ "$response" == "200" ]]; then
      cd /
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

