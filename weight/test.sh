#!/bin/sh
echo "INITIATING TEST as weight team"
sleep 1.5
echo "STARTING HEALTH TEST as weight team"
output=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/health")

if [ "$output" = '"APP ON AIR"' ]; then
    echo "Passed the health assesment"
    

elif [ "$output" = '"OK 200 & BAD Connection"' ];then
		echo "failed health to database assesment"
        
else
    echo "failed health assesment"
fi
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
output=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/health")
if [ "$output" = '"APP ON AIR"' ]; then
    success=$((success+1))
elif [ "$output" = '"OK 200 & BAD Connection"' ]; then
		echo "failed health to database assesment"
        exit 2
else
    echo "failed health assesment"
	exit 1
fi
################################################################################################################################
#POST WEIGHT TEST
post_success=0
#Test #1
echo "STARTING POST WEIGHT TEST"
sleep 1
truncate(){
	docker exec -it test-my_data-1  mysql -u root -proot weight -e "TRUNCATE TABLE transactions"
 }
truncate >> /dev/null
test1=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
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
	post_success=$((post_success+1))

else
	echo " Failed Test POST/weight#1 - Could not POST an IN Request."
	exit 1
fi
#Test #2
test2=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
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
	post_success=$((post_success+1))
else
	echo "Failed Test POST/weight#2 - Could not POST an OUT Request, failed to update an existing IN request"
	exit 1
fi
#Test3
test3=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
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
	post_success=$((post_success+1))
else
	echo "Failed Test POST/weight#3 - Could POST an OUT Request on existing OUT request with FORCE=FALSE"
	exit 1
fi
#Test 4 
test4=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"out",
"containers":"C-35434",
"truck":"T-SystemTest",
"force":true,
"weight":1960,
"unit":"kg"
}')
expected_result4='{
  "bruto": 3000,
  "id": 1,
  "neto": 744,
  "truck": "T-SystemTest",
  "truckTara": 1960
}'
if echo "$test4" | grep -q "$expected_result4"
then
	post_success=$((post_success+1))
else
	echo "Failed Test POST/weight#4 - Could not Force an OUT Request on existing OUT request"
fi
#Test5
test51=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
--header 'Content-Type: application/json' \
--data-raw '{
"direction":"in",
"containers":"C-35434",
"truck":"T-SystemTest",
"weight":1500,
"unit":"kg"
}')

test52=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/weight" \
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
	post_success=$((post_success+1))
else
	echo "Failed Test POST/weight#5 - Could update an IN request without using force"
fi
################################################################################################################################
# Test Session ID
session_success=0
echo "STARTING GET SESSION TEST as weight team"
sleep 3
#Test 1
test1=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/session/1")
expected_result1='
  {
    "bruto": 3000,
    "direction": "out",
    "id": 1,
    "neto": 744,
    "truck": "T-SystemTest",
    "truckTara": 1960
  }
'
if echo "$test1" | grep -q "$expected_result1"
then
    session_success=$((session_success+1))
else
    echo "Failed test #1 - Failed to view a session with a truck heading OUT"
    exit 1
fi
# Test 2
test2=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/session/2")
expected_result2='
  {
    "bruto": 1500,
    "direction": "in",
    "id": 2,
    "truck": "T-SystemTest"
  }
'
if echo "$test2" | grep -q "$expected_result2"
then
    session_success=$((session_success+1))
else
    echo "Failed test #2 - Failed to view a session with a truck heading IN"
    exit 1
fi
# if [ $? -eq 0 ]; then
#     echo "Success!"
#     echo ${session_success}/2
# else
#     echo "Failed..."
# fi
################################################################################################
# Unknown Test
unknown_success=0
echo "STARTING GET UNKNOWN TEST as weight team"
sleep 3
#PREP
test_prep(){
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id, unit) VALUES ("K-Test1", "lbs")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id, unit) VALUES ("K-Test2", "kg")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id) VALUES ("K-Test3")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id) VALUES ("K-Test4")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id) VALUES ("K-Test5")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id, unit) VALUES ("K-Test6", "lbs")'
    docker exec -it test-my_data-1  mysql -u root -proot weight -e 'INSERT INTO containers_registered (container_id, unit) VALUES ("K-Test7", "lbs")'
}
test_prep >> /dev/null # Inserts few containers with no weight information
# Test 1 
test1=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/unknown")
expected_result1='
  "K-Test1",
  "K-Test2",
  "K-Test3",
  "K-Test4",
  "K-Test5",
  "K-Test6",
  "K-Test7"
'
if echo "$test1" | grep -q "$expected_result1"
then
    unknown_success=$((unknown_success+1))
else
    echo "Failed to fetch unknown containers - containers with no documented weight information"
    exit 1
fi

# if [ $? -eq 0 ]
# then
#     echo "Success !"
#     echo ${unknown_success}/1
# else
#     echo "Failure..."
# fi
################################################################################################################################
# Test Get Item

item_success=0
echo "STARTING GET ITEM TEST as weight team"
sleep 3
test1=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/item/K-8263")
expected_result1='
  "id": "K-8263",
  "instance": "container",
  "sessions": 
    1,
    2,
    3
  ,
  "tara": 666
'
if echo "test1" | grep -q "$expected_result1"
then    
    item_success=$((item_success+1))
else
    echo "Failed Test #1 - Could not find Container Information"
    exit 1
fi
# Test 2 
test2=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/item/T-SystemTest")
expected_result2='
  "id": "T-SystemTest",
  "instance": "truck",
  "sessions":
    1,
    3,
    4
  ,
  "tara": "na"
'
if echo "$test2" | grep -q "$expected_result2"
then
    item_success=$((item_success+1))
else
    echo "Failed Test #2 - Could not find truck information"
    exit 1
fi

# Test 3 
test3=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/item/T-NotFound")
expected_result3="Not Found T-NotFound"
if echo $test3 | grep -q "$expected_result3"
then
    item_success=$((item_success+1))
else
    echo "Failed Test #3 - Either found an unfindable item or failed to report it in the desired format "
fi
# if [ $? -eq 0 ]; then

#     echo "Success"
#     echo ${item_success}/2
# else
#     echo "Failure"
# fi
################################################################################################################################

batch_success=0
echo "STARTING BATCH WEIGHT TEST as weight team"
sleep 3
test1=$(curl "ubuntu@ec2-3-10-71-229.eu-west-2.compute.amazonaws.com:${WEIGHT_APP_PORT}/batch-weight" \
--form 'filename="containers3.json"' \
--form 'password="root"')
expected_result1="containers3.json uploaded successfully"
if echo "$test1" | grep -q "$expected_result1"
then
    batch_success=$((batch_success+1))
else
    echo "Failed Test #1 - Failed to load the MySQL database using json file"
    exit 1
fi
test2=$(curl --location --request POST 'localhost:8083/batch-weight' \
--form 'filename="containers2.csv"' \
--form 'password="root"')
expected_result2="containers2.csv uploaded successfully"

if echo "$test2" | grep -q "$expected_result2"
then
    batch_success=$((batch_success+1))
else
    echo "Failed Test #2 - Failed to load the MySQL database using csv file"
fi

test3=$(curl --location --request POST 'localhost:8083/batch-weight' \
--form 'filename="containers2.csv"' \
--form 'password="wrongpass"')
expected_result3="Wrong Password"

if echo "$test3" | grep -q "$expected_result3"
then
    batch_success=$((batch_success+1))
else
    echo "Failed Test #3 - Either load a MySQL database using a wrong password or failed to report it in the desired format."
fi

test4=$(curl --location --request POST 'localhost:8083/batch-weight' \
--form 'filename="file.txt"' \
--form 'password="root"')
expected_result4="can't open this file"
if echo "$test4" | grep -q "$expected_result4"
then
    batch_success=$((batch_success+1))
else
    echo "Failed Test #4 - Either load a MySQL database using a non-standard file or failed to report it in the desired format."
    exit 1
fi

# if [ $? -eq 0 ]
# then
#     echo "Success"
#     echo ${batch_success}/4
# else
#     echo "Failure"
# fi

################################################################################################################################
#Final Conclusion
if [ $? -eq 0 ]
then
	echo "Success !"
	echo ${success}/1
	echo ${post_success}/5
	echo ${session_success}/2
	echo ${unknown_success}/1
	echo ${item_success}/3
	echo ${batch_success}/4

else
	echo " Failure :(..."
fi
