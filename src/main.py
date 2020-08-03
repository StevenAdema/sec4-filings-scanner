# package used to execute HTTP POST request to the API
import json
import urllib.request

# Open config file containing private token
with open('.\config\credentials.json') as f:
    credentials = json.load(f)
# API Key
TOKEN =  credentials["credentials"]["key"]
# API Endpoint
API = 'https://api.sec-api.io?token=' + TOKEN

# Create filter parameters to send to the API 
filter = "formType:\"4\" AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[2020-07-31 TO 2020-08-31]"
payload = {
  "query": { "query_string": { "query": filter } },
  "from": "0",
  "size": "10000",
  "sort": [{ "filedAt": { "order": "desc" } }]
}

# Format payload to JSON bytes
jsondata = json.dumps(payload)
jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes

# Send request 
req = urllib.request.Request(API)

# set the correct HTTP header: Content-Type = application/json
req.add_header('Content-Type', 'application/json; charset=utf-8')
# set the correct length of your request
req.add_header('Content-Length', len(jsondataasbytes))

# send the request to the API
response = urllib.request.urlopen(req, jsondataasbytes)

# read the response 
res_body = response.read()
# transform the response into JSON
filings = json.loads(res_body.decode("utf-8"))

# write json response to file.
with open('.\data\data.json', 'w') as f:
    json.dump(filings, f)

# print JSON 
print(filings)
