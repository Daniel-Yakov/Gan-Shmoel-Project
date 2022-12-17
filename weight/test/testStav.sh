#!/bin/bash
success=0

WEIGHT_IP=localhost

if [ $# -gt 0 ];then
	WEIGHT_IP=$1
fi

echo "INITIATING TEST as weight team"
sleep 1
echo "STARTING HEALTH TEST as weight team"
sleep 3
#Test Health
output=$(curl "${WEIGHT_IP}:8083/health")

if [ "$output" = '"APP ON AIR"' ]; then
    success=$((success+1))


elif [ "$output" = '"OK 200 & BAD Connection"' ]; then
		echo "failed health to database assesment"
        exit 2
else
    echo "failed health assesment"
	exit 1
fi

#Test #1

echo "STARTING HEALTH TEST as weight team"

sleep 1

function truncate(){
	docker exec -it weight-my_data-1 mysql -u root -proot weight -e "TRUNCATE TABLE transactions"
}
truncate
test1=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"in",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":3000,
"unit":"kg"
}')
expected_result1='{
  "bruto": 3000,
  "id": 1,
  "truck": "T-SystemTest"
}'
if echo "$test1" | grep -q "$expected_result1"
then
	success=$((success+1))

else
	echo " Failed Test POST/weight#1 - Could not POST an IN Request."
	exit 1
fi
#Test #2
test2=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"out",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":704,
"unit":"kg"
}')
expected_result2='{
  "bruto": 3000,
  "id": 1,
  "neto": 2000,
  "truck": "T-SystemTest",
  "truckTara": 704
}'
if echo "$test2" | grep -q "$expected_result2"
then
	success=$((success+1))
else
	echo "Failed Test POST/weight#2 - Could not POST an OUT Request, failed to update an existing IN request"
	exit 1
fi
#Test3
test3=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"out",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":1960,
"unit":"kg"
}')
expected_result3="Error"
if echo "$test3" | grep -q "$expected_result3"
then
	success=$((success+1))
else
	echo "Failed Test POST/weight#3 - Could POST an OUT Request on existing OUT request with FORCE=FALSE"
	exit 1
fi
#Test 4 
test4=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"out",
"containers":"C-35434",
"truck":"T-SystemTest",
"force":true,
"weight":1960,
"unit":"kg"
}')
expected_result4="{
  "bruto": 3000,
  "id": 1,
  "neto": 744,
  "truck": "T-SystemTest",
  "truckTara": 1960
}"
if echo "$test4" | grep -q "$expected_result4"
then
	success=$((success+1))
else
	echo "Failed Test POST/weight#4 - Could not Force an OUT Request on existing OUT request"
fi
#Test5
test51=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"in",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":1500,
"unit":"kg"
}')

test52=$(curl --location --request POST "${WEIGHT_IP}:8083/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"in",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":3000,
"force":false,
"unit":"kg"
}')
expected_result5="Error"
echo "$test51" >> /dev/null
if echo "$test52" | grep -q "$expected_result5"
then
	success=$((success+1))
else
	echo "Failed Test POST/weight#5 - Could update an IN request without using force"
fi

#Test 6




#Final Conclusion
if [ $? -eq 0 ]
then
	echo "Success !"
	echo $success
else
	echo " Failure :(..."
fi

