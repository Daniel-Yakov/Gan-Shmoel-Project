#!/bin/sh
echo "INITIATING TEST as weight team"
sleep 1.5
echo "STARTING HEALTH TEST as weight team"
output=$(curl "http://ec2-18-168-15-244.eu-west-2.compute.amazonaws.com/:$WEIGHT_APP_PORT/health)

if [ "$output" = '"APP ON AIR"' ]; then
    echo "Passed the health assesment"
    echo "Passed the health assesment"

elif [ "$output" = '"OK 200 & BAD Connection"' ]
		echo "failed health to database assesment"
        
else
    echo "failed health assesment"
fi
