#!/bin/bash

set -xe
# diff audit files
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$(${DIR}/audit.py -f $1 -s buildId | json_pp --json_opt=canonical,pretty > $1.readable) &
pid1=$!
$(${DIR}/audit.py -f $2 -s buildId | json_pp --json_opt=canonical,pretty > $2.readable) &
pid2=$!

wait $pid1
wait $pid2

if [ $# -gt 2 ]; then
   $3 $1.readable $2.readable
else
   diff -Nurp $1.readable $2.readable
fi

