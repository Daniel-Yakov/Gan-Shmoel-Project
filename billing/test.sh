#!/bin/sh
echo "INITIATING TEST"
SCORE=0
sleep 1
echo "STARTING HEALTH TEST"
sleep 1
output=$(curl "http://localhost:$BILLING_APP_PORT/health")

echo $output | grep -q -o "OK" 

if [ $? -eq 0 ]; then
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

search_string="Welcome"
form_data="Pname=value"
output=$(curl -X POST "http://localhost:$BILLING_APP_PORT/provider" -F Pname=test)
echo $output | grep -q -o "ID"


if [ $? -eq 0  ]; then
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
output=$(curl -X GET "http://localhost:$BILLING_APP_PORT/rates" -H "Content-Type: application/json")
echo $output | grep -q -o "File downloaded successfully" 

if [ $? -eq 0  ]; then
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