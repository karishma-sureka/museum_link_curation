import requests
from requests.auth import HTTPBasicAuth

"""
Register User -
-------------

curl -X POST http://localhost:5000/v1/user -H "Content-Type: application/json" -d '{"username":"ksureka@usc.edu","password":"kma123"}'


{
    "Location": "http://localhost:5000/v1/user/1", 
    "username": "ksureka@usc.edu"
}
"""
payload = '{"username":"ksureka@usc.edu","password":"kma123"}'
header={'Content-Type': 'application/json'}
r = requests.post("http://localhost:5000/v1/user", data=payload, headers=header)

print(r.text)

"""
Login Registered User -
---------------------

curl -X GET http://localhost:5000/v1/user -H "Content-Type: application/json" -d '{"duration":3600}' -u ksureka@usc.edu:kma123


{
    "token": {
        "duration": 3600, 
        "value": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ2MTgzNjg4NSwiaWF0IjoxNDYxODMzMjg1fQ.eyJpZCI6MX0.H_Y4x3lxJmI7xbfR9RwvVMhdLfw29vI6lJPOmz00F0s"
    }, 
    "user": {
        "name": "", 
        "rating": 5, 
        "tags": [], 
        "username": "ksureka@usc.edu"
    }
}
"""

payload = '{"duration":3600}'
header={'Content-Type': 'application/json'}
r = requests.get("http://localhost:5000/v1/user", data=payload, headers=header, auth=HTTPBasicAuth('ksureka@usc.edu', 'kma123'))

print(r.text)

"""
Update Registered User Profile-
------------------------------

curl -X PUT http://localhost:5000/v1/user -H "Content-Type: application/json" -d '{"name":"Karishma Sureka","rating":5,"tags":["dbpedia","npg"]}' -u ksureka@usc.edu:kma123


{
    "name": "Karishma Sureka", 
    "rating": 5, 
    "tags": [
        "dbpedia", 
        "npg"
    ], 
    "username": "ksureka@usc.edu"
}
"""
payload = '{"name":"Karishma Sureka","rating":5,"tags":["dbpedia","npg"]}'
header={'Content-Type': 'application/json'}
r = requests.put("http://localhost:5000/v1/user", data=payload, headers=header, auth=HTTPBasicAuth('ksureka@usc.edu', 'kma123'))

print(r.text)

"""
Single/Bulk Question Request-
----------------------------

curl -X GET http://localhost:5000/v1/question -H "Content-Type: application/json" -d '{"stats":"True"}' -u ksureka@usc.edu:kma123
curl -X GET http://localhost:5000/v1/question -H "Content-Type: application/json" -d '{"bulk":10,"stats":"True"}' -u ksureka@usc.edu:kma123

[]

"""
payload = '{"bulk":10,"stats":"True"}'
header={'Content-Type': 'application/json'}
r = requests.get("http://localhost:5000/v1/question", data=payload, headers=header, auth=HTTPBasicAuth('ksureka@usc.edu', 'kma123'))

print(r.text)

"""
Submit Answer Request-
---------------------

curl -X PUT http://localhost:5000/v1/answer -H "Content-Type: application/json" -d '{"value":"1","comment":"Just another comment","qid":"570eec1df6bf2d1e58a88479"}' -u ksureka@usc.edu:kma123

{
    "message": [
        "Question not found for qid: ", 
        "570eec1df6bf2d1e58a88479"
    ]
}

"""

payload = '{"value":"1","comment":"Just another comment","qid":"570eec1df6bf2d1e58a88479"}'
header={'Content-Type': 'application/json'}
r = requests.put("http://localhost:5000/v1/answer", data=payload, headers=header, auth=HTTPBasicAuth('ksureka@usc.edu', 'kma123'))

print(r.text)






