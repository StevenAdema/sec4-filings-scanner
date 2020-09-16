import json
import pandas as pd
import urllib.request
pd.options.mode.chained_assignment = None  # supress copy warning


with open(r'..\config\config.json') as f:
    config = json.load(f)


def get_filings():
    TOKEN = config["credentials"]["key"]
    API = 'https://api.sec-api.io?token=' + TOKEN

    # Create filter parameters to send to the API
    filter = "formType:\"4\" AND ticker:(NOT \"\") AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[2019-09-10 TO 2019-09-10]"
    payload = {
        "query": {"query_string": {"query": filter}},
        "from": "0",
        "size": "200",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    # Format payload to JSON bytes
    jsondata = json.dumps(payload)
    jsondataasbytes = jsondata.encode('utf-8')

    # Send request
    print('sending request')
    req = urllib.request.Request(API)

    # set the correct HTTP header: Content-Type = application/json
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    # set the correct length of your request
    req.add_header('Content-Length', len(jsondataasbytes))

    # send the request to the API
    response = urllib.request.urlopen(req, jsondataasbytes)

    # read the response
    response_body = response.read()
    # transform the response into JSON
    filings = json.loads(response_body.decode("utf-8"))
    return filings


def get_filings_over_period(d1, d2):
    """Takes two dates and returns all sec-4 filings made during that period

    Args:
        d1: a date string of the start period (inclusive)
        d2: a date string of the end period (exclusive)

    Returns
        Returns a dataframe containing all sec4 filings over the specified period.
    """
    TOKEN = config['credentials']['key']
    API = 'https://api.sec-api.io?token=' + TOKEN

    d = d1
    filter = 'formType:\"4\" AND ticker:(NOT \"\") AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:' + d

    payload = {
        "query": {"query_string": {"query": filter}},
        "from": "0",
        "size": "200",
        "sort": [{"filedAt": {"order": "ASC"}}]
    }

    # Format payload to JSON bytes
    jsondata = json.dumps(payload)
    jsondataasbytes = jsondata.encode('utf-8')

    # Send request
    print('sending request')
    req = urllib.request.Request(API)

    # set the correct HTTP header: Content-Type = application/json
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    # set the correct length of your request
    req.add_header('Content-Length', len(jsondataasbytes))

    # send the request to the API
    response = urllib.request.urlopen(req, jsondataasbytes)

    # read the response
    response_body = response.read()
    # transform the response into JSON
    filings = json.loads(response_body.decode("utf-8"))
    last_item = len(filings['filings']) - 1
    print(filings['filings'][last_item]['filedAt'])

    return filings
