#!/bin/bash
#
# usage: bash ./zip_dir.sh drive/dataset/tsugu00/
# extract: tar -xvJf TARGET.tar.xz
#

set -eu
set -o pipefail

trap 'echo "error:$0($LINENO) \"$BASH_COMMAND\" \"$@\""' ERR

[ 1 -eq $# ]

DIR=$1

DIR_NAME=$(basename ${DIR})

pushd $(dirname ${DIR})
tar -cvJf ${DIR_NAME}_$(date '+%Y%m%d_%Hh%Mm').tar.xz ./${DIR_NAME} > /dev/null
#tar -cf - ./${DIR_NAME} | xz -9 -c - > ${DIR_NAME}_$(date '+%Y%m%d_%Hh%Mm').tar.xz

popd


