#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

outdir="${__dir}/module/lambda"
zipname="sns-to-slack.zip"

pushd sns-to-slack

zip -u "${outdir}/${zipname}" lambda_function.py

pushd $VIRTUAL_ENV/lib/python2.7/site-packages

zip -u -r "${outdir}/${zipname}" . \
  --exclude pip\* \
  --exclude setuptools\* \
  --exclude virtualenv\*

popd

popd
