#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

outdir="${__dir}/module/lambda"
zipname="sns-to-slack.zip"

pushd sns-to-slack
pipenv install
pipenv run pip install -r <(pipenv lock -r) --target _build/
cp lambda_function.py _build/

pushd _build
zip -r ${zipname} *
cp ${zipname} ${outdir}
popd

popd
