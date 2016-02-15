#!/bin/bash
#
# fifo-write.sh <str> <filename> - non-blocking write to named pipe
#
# Writes string <str> to filesystem FIFO (named pipe)
# identified by <filename>. If the <filename> is not FIFO,
# it returns -2. If there is no reader on FIFO, it will still
# write to it in non-blocking mode.
#

if [ $# -ne 2 ]; then
    echo "fifo-write.sh <str> <filename>" 1>&2
    exit -1
fi

if [ ! -p "$2" ]; then
    echo "File $2 is not a named pipe."
    exit -2
fi

# open filename non-blocking as descriptor 4
exec 4<>"$2"

echo "$1" >&4
