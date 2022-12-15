#!/bin/bash
echo "INITIATING TEST"
sleep 1.5s
echo "STARTING HEALTH TEST"
output=$(curl "http://ubuntu@ec2-18-168-15-244.eu-west-2.compute.amazonaws.com:$BILLING_APP_PORT/health")
if [ "$output" = '"OK"' ]; then
    echo "Passed the health assesment">>logger.txt
    echo "Passed the health assesment"
else
    echo "failed health assesment">>logger.txt
fi

