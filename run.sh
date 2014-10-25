#!/bin/bash

RUN_AI="python python/game.py"

# for Java, uncomment this line:
# RUN_AI="java -jar java/target/AWAP-0.0.1-SNAPSHOT.jar"

# for CPP, uncomment this line:
# RUN_AI="./cpp/game"

TEAM_ID="woofwoof"
FAST=0

trap "pkill -P $$" SIGTERM SIGKILL EXIT

while getopts "fs:t:" option;
do
    case $option in
        f) FAST=1 ;;
        s) RUN_AI="$RUN_AI $OPTARG" ;;
        t) TEAM_ID=$OPTARG ;;
    esac
done

python client.py "$RUN_AI" $TEAM_ID $FAST &

wait
