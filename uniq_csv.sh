#!/usr/bin/env bash

# Reads stdin pipe. Outputs comma separated columns.
# Removes duplicate rows (ignoring the first one, which supposed to be a timestamp).

uniq -f 1 <&0| grep -v "^#" | awk -v OFS=',' '{ for (i=1; i<=NF; i++) printf "%s%s", $i, (i<NF ? OFS : ORS)}'
