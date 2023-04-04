#!/usr/bin/env bash

# Download Grobid
cd $HOME
wget https://github.com/kermitt2/grobid/archive/0.6.1.zip
unzip 0.6.1.zip
rm 0.6.1.zip
cd $HOME/grobid-0.6.1
./gradlew clean install

## Start Grobid
./gradlew run
