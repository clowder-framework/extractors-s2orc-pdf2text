#!/usr/bin/env bash

GrobidHome="$HOME/grobid-0.6.1/"

if [[ -d "$GrobidHome" ]]; then
  cd $GrobidHome
  # check if gradle is installed
  if [[ $(./gradlew -v) ]]; then
    # gradle is installed. run gradle
    ## Start Grobid
    ./gradlew run
  else
    # install and run gradle
    ./gradlew clean install
    ./gradlew run
  fi
else
  # need to get and install gradlew
  apt-get install -y wget unzip
  cd $HOME
  wget https://github.com/kermitt2/grobid/archive/0.6.1.zip
  unzip 0.6.1.zip
  rm 0.6.1.zip
  cd $HOME/grobid-0.6.1
  ./gradlew clean install

  ## Start Grobid
  ./gradlew run
fi
