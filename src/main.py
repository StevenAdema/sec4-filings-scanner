import json
import sec4_reader as reader
import pandas as pd
pd.options.mode.chained_assignment = None  # supress copy warning
import numpy as np
import urllib.request


def main():
    """
    Main method to run the script
    """

    # Temp Removed to Reduce API calls
    # # Open config file containing private token
    with open(r'..\config\config.json') as f:
        config = json.load(f)
    # API Key
    TOKEN = config["credentials"]["key"]
    # API Endpoint
    API = 'https://api.sec-api.io?token=' + TOKEN

    # Create filter parameters to send to the API
    filter = "formType:\"4\" AND ticker:(NOT \"\") AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[2020-08-12 TO 2020-08-12]"
    payload = {
        "query": {"query_string": {"query": filter}},
        "from": "0",
        "size": "200",
        "sort": [{"filedAt": {"order": "desc"}}]
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
    response_body = response.read()
    # transform the response into JSON
    filings = json.loads(response_body.decode("utf-8"))

    # write json response to file.
    with open(r'..\data\data.json', 'w') as f:
        json.dump(filings, f)

    # Use saved JSON
    # with open('.\\data\\data.json', 'r') as f:
    with open(r'..\data\data.json', 'r') as f:
        filings = json.load(f)

    # Load results to DataFrame
    df = pd.DataFrame(filings['filings'])

    # Create DataFrame
    df = df[config["dataframe"]["columns_shortlist"]]

    # Add columns additional columns
    for new_column in config["dataframe"]["columns_new"]:
        df[new_column] = np.nan

    df = df[config["dataframe"]["column_order"]]
    df = df[df['companyName'] != df['rptOwnerName']]

    df2 = df[0:0]
    reader.read_sec4_to_dataframe(df, df2)

    df2 = df2[df2['companyName'] != df2['rptOwnerName']]

    # Write df to CSV
    # df2 = df2[df2['expirationDate'] != '']
    df2.to_csv(r'..\data\data.csv',
               index=False, encoding="utf-8", sep='|')


if __name__ == "__main__":
    main()
