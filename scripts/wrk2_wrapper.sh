# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash


RUN_RPS=()
EXEC_DURATION=60
EXEC_THREADS=4
EXEC_CONNECTIONS=8
EXEC_HOST=""

function iterate_and_execute() {
    local NUM_EXECUTIONS=$(echo "${#RUN_RPS[@]}")

    NODE_NO_HTTP=${EXEC_HOST#http://*}
    NODE_NO_PORT=${NODE_NO_HTTP%:*}

    for RPS in "${RUN_RPS[@]}"; do
        run_wrk2 ${RPS} ${EXEC_THREADS} ${EXEC_CONNECTIONS} ${EXEC_DURATION}  ${EXEC_HOST}
    done

    mv test-result.csv test-result-${NODE_NO_PORT}.csv
}

function run_wrk2() {
    local RPS=$1
    local THREADS=$2
    local CONNECTIONS=$3
    local DURATION=$4
    local EXEC_HOST=$5

    # Run wrk2
    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION}s -R${RPS} --latency -s runner.lua ${EXEC_HOST}
}

# Collect all run rate arguments
while getopts ":r:d:t:c:h:" opt; do
    case $opt in
        r)
            RPS="$OPTARG"
            RUN_RPS+=(${RPS})
            ;;
        d)
            # Optional
            EXEC_DURATION="$OPTARG"
            ;;
        t)
            # Optional
            EXEC_THREADS="$OPTARG"
            ;;
        c)
            # Optional
            EXEC_CONNECTIONS="$OPTARG"
            ;;
        h)
            EXEC_HOST="$OPTARG"
            ;;
        *)
            echo $"Usage: $0 {r: rate as requests per second|d: test duration in seconds (default: 60)|t: threads for the test (default: 4)|c: connections to open (defaults to 8)}"
		    exit 1
    esac
done

iterate_and_execute
