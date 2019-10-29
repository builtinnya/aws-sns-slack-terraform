#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

outdirs="${__dir}/module/lambda ${__dir}/module-v0.12/lambda"
zipname="sns-to-slack.zip"

pushd sns-to-slack
pipenv install
pipenv run pip install -r <(pipenv lock -r) --target _build/
cp lambda_function.py _build/

pushd _build
find . -name '*.pyc' -delete
rm -f ${zipname}
zip -r ${zipname} *
for outdir in $outdirs; do cp ${zipname} ${outdir}; done
popd

popd
