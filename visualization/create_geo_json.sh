#!/usr/bin/env bash
(echo -n "var d="; jq '.features|=map(.properties|=(.+$l[0][.GM_NAAM]))' --slurpfile l <(jq '
.mapping
| map({(.municipality_name):.})
| add
| with_entries(.key|=($m[0][.]//.))' ./exports/error_stats_total.json --slurpfile m ./visualization/incorrect_name_mncp_map.json)  ./visualization/gemeente_2019.geo.json -c | tr -d '\n';echo ";")> ./visualization/error_stats.geo.json.js

(echo -n "var p="; jq '.features|=map(.properties|=(.+$l[0][.PV_NAAM]))' --slurpfile l <(jq '
.mapping
| map({(.province_name):.})
| add
| with_entries(.key|=($m[0][.]//.))' ./exports/error_stats_province.json --slurpfile m ./visualization/incorrect_name_province_map.json)  ./visualization/provincie_2019.geo.json -c | tr -d '\n';echo ";")> ./visualization/error_stats_province.geo.json.js
