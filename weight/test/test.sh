#!/bin/bash
echo "INITIATING TEST as weight team"
sleep 1.5s
echo "STARTING HEALTH TEST as weight team"
output=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com /:$WEIGHT_APP_PORT/health)

if [ "$output" = '"APP ON AIR"' ]; then
    echo "Passed the health assesment">>logger.txt
    echo "Passed the health assesment"

elif [ "$output" = '"OK 200 & BAD Connection"' ]; then
		echo "failed health to database assesment">>logger.txt

else
    echo "failed health assesment">>logger.txt
fi
