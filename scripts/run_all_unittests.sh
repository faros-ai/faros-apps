#!/usr/bin/env bash
# Run all app unittest suites
# Note: run pip install -r requirements.txt to ensure all app requirements

set -o errexit
set -o nounset

SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(cd "$(dirname "${SCRIPT_DIR}")" && pwd)"
APPS_BASE_DIR="${ROOT_DIR}/apps"

for APP_DIR in ${APPS_BASE_DIR}/dora-metrics/* ; do
		if [ -d "${APP_DIR}" ] ; then
	    echo "Running tests in app directory ${APP_DIR}"
  	  python3 -m unittest discover -s ${APP_DIR}
		fi
done

for APP_DIR in ${APPS_BASE_DIR}/* ; do
    echo "Running tests in app directory ${APP_DIR}"
    python3 -m unittest discover -s ${APP_DIR}
done

