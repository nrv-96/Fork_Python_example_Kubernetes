#!/bin/bash

# This wrapper script exits to help setup module local environment
# It pulls and run the actual script from general-resources in Nexus3

SCRIPT_NAME='module-setup.sh'

rm -rf general-resources && mkdir -p general-resources
curl -v -k -L \
  'https://nexus-tools.swacorp.com/service/rest/v1/search/assets/download?sort=version&repository=releases&group=com.swacorp.ccplat.swa-common.ccp&name=general-resources&maven.extension=zip' \
  --output ./general-resources/general-resources.zip
unzip -o ./general-resources/general-resources.zip -d ./general-resources
mv ./general-resources/resources/$SCRIPT_NAME ./; \
  sh $SCRIPT_NAME; \
  rm $SCRIPT_NAME; \
  rm -rf general-resources
