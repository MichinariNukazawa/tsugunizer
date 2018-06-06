#!/bin/bash
#
# usage: bash ./zip_dir.sh drive/dataset/tsugu00/
#

set -eu
set -o pipefail

trap 'echo "error:$0($LINENO) \"$BASH_COMMAND\" \"$@\""' ERR

[ 1 -eq $# ]

DIR=$1

DIR_NAME=$(basename ${DIR})

pushd $(dirname ${DIR})
zip -r9 ${DIR_NAME}_$(date '+%Y%m%d_%Hh%Mm').zip ./${DIR_NAME} > /dev/null

popd


