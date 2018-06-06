#!/bin/bash
#
#

set -eu
set -o pipefail

trap 'echo "error:$0($LINENO) \"$BASH_COMMAND\" \"$@\""' ERR

[ 2 -eq $# ]

LIST_FILE=$1
SRC_DIR=$2
DST_DIR=$(dirname ${SRC_DIR})/$(basename ${SRC_DIR})_copylist/

[ -f ${LIST_FILE} ]
[ -d ${SRC_DIR} ]

mkdir ${DST_DIR}

cat ${LIST_FILE} | while read LINE || [ -n "${LINE}" ]; do
	#echo "LINE: ${LINE}"
	regexp="^([0-9]+)"
	if [[ $LINE =~ $regexp ]] ; then
		IMAGE_ID=${BASH_REMATCH[1]}
		#echo ${IMAGE_ID}
		cp ${SRC_DIR}/${IMAGE_ID}* ${DST_DIR}
	fi
done


