#!/usr/bin/env bash

failed_no=$(grep -c "Failed" $1)
passed_no=$(grep -c "Passed" $1)

#echo Failed = $failed_no
#echo Passed = $passed_no

total=$((failed_no + passed_no))
FINAL_COUNT=$failed_no'/'$total

echo $FINAL_COUNT