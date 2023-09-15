#!/bin/sh

dir="data/gtab_res"
name=${1//'_'/' '}
query="$name Sexual harassment"
output="$dir/$1.json"

[[ ! -d "$dir" ]] && mkdir -p "$dir"

echo "query: $query"

gtab-set-active "google_anchorbank_geo=_timeframe=2016-01-01 2018-07-31.tsv"
gtab-query "$query" --results_file "$PWD/$output"
