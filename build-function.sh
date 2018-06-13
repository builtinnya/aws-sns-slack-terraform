#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

default_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/module/lambda"

outdir="${1:-$default_dir}"
zipname="sns-to-slack.zip"

pushd sns-to-slack
pipenv install
pipenv run pip install -r <(pipenv lock -r) --target _build/
cp lambda_function.py notification.py _build/

pushd _build
zip -r -X ${zipname} *
cp ${zipname} ${outdir}
popd

popd
