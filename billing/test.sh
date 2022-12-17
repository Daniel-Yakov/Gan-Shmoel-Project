#!/bin/sh
echo "INITIATING TEST"
SCORE=0
sleep 1
echo "STARTING HEALTH TEST"
sleep 1
output=$(curl "http://ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:$BILLING_APP_PORT/health")
if [ "$output" = '"OK"' ]; then
    tput setaf 2
    echo "Passed the health assesment"
    SCORE=$((SCORE+1))
    tput sgr0

else
    tput setaf 1
    echo "failed health assesment"
    tput sgr0

fi

echo "Creating a Provider Example"
sleep 1
output=$(curl -X POST "http://ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:$BILLING_APP_PORT/provider" -H "Content-Type: application/json")
id_value=$(echo $output | awk -F '"id":' '{ print $2 }' | awk -F '}' '{ print $1 }')
echo $id_value

if [ $id_value -gt 10000 ]; then
    tput setaf 2
    echo "Data base test finished successfully"
    SCORE=$((SCORE+1))
    tput sgr0

else
    tput setaf 1
    echo "failed database  assesment"
    tput sgr0
fi



echo "Starting Volume Check"
sleep 1
output=$(curl -X GET "http://ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:$BILLING_APP_PORT/rates" -H "Content-Type: application/json")
status=$(echo $output | awk -F '"success":' '{ print $2 }' | awk -F '}' '{ print $1 }')


echo $status
if [ "$status" = ' "File downloaded successfully" ' ]; then
    tput setaf 2
    echo "Passed the Volume assesment"
    SCORE=$((SCORE+1))
    tput sgr0

else
    tput setaf 1
    echo "failed Volume assesment"
    tput sgr0

fi


echo "TEST SCORE IS $SCORE"

if [ $SCORE -eq 3 ]; then
    tput setaf 2
    echo "Passed"
    tput sgr0
    exit 0
else
    tput setaf 1
    echo "Fail"
    tput sgr0
    exit 1
fi