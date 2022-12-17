#!/bin/bash

url=$1

curl -X POST "$url/provider?name=yotam"
curl -X POST "$url/truck?id=10001&plate=10001"
curl -X POST "$url/truck?id=10001&plate=10002"
curl -X GET "$url/bill/10001"