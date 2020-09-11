import json
import sec4_reader as reader
import pandas as pd
pd.options.mode.chained_assignment = None  # supress copy warning
import numpy as np
import urllib.request
np.set_printoptions(linewidth=300)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 30)


def main():
    """
    Main method to run the script
    """

    # Open config file containing private token
    with open(r'..\config\config.json') as f:
        config = json.load(f)

    # Url for API call
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

    # write json response to file.
    with open(r'..\data\data.json', 'w') as f:
        json.dump(filings, f)

    # Use saved JSON
    with open(r'..\data\data.json', 'r') as f:
        filings = json.load(f)

    print('generate DataFrame')
    # Load results to DataFrame
    df = pd.DataFrame(filings['filings'])
    print(df.shape)

    # Create DataFrame
    df = df[config["dataframe"]["columns_shortlist"]]

    # Add columns additional columns
    for new_column in config["dataframe"]["columns_new"]:
        df[new_column] = np.nan

    df = df[config["dataframe"]["column_order"]]
    df = df[df['companyName'] != df['rptOwnerName']]

    print('read to new DataFrame')
    df = reader.filter_has_ticker(df)
    df2 = df[0:0]
    print(df.shape)
    reader.read_sec4_to_dataframe(df, df2)
    print('read')
    print(df2.shape)

    # df2.to_pickle(r'..\data\data.pkl')
    # df2 = pd.read_pickle(r'..\data\data.pkl')

    df2 = reader.get_only_bought(df2)

    print(df2)

    # Write df to CSV
    # df2 = df2[df2['expirationDate'] != '']
    df2.to_csv(r'..\data\data.csv',
               index=False, encoding="utf-8", sep='|')


if __name__ == "__main__":
    main()
