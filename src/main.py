import json
import pandas as pd
import urllib.request
from xml_parser import XmlParser
import xml.etree.cElementTree as ET
import re
import time


def main():

    ''' Temp Removed to Reduce API calls
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
    '''

    # with open('.\\data\\data.json', 'r') as f:
    with open('..\data\data.json', 'r') as f:
        filings = json.load(f)

    # Load results to DataFrame
    df = pd.DataFrame(filings['filings'])

    xml = df['linkToTxt'].iloc[0]
    xml_root = download_xml(xml)

    nonDerivativeTransactions = xml_root.findall("./derivativeTable/derivativeTransaction")
    l =[]

    for t in nonDerivativeTransactions:
        securityTitle = t.find('./securityTitle/value').text
        transactionDate = t.find('./transactionDate/value').text
        exerciseShares = t.find('./transactionAmounts/transactionShares/value').text
        exercisePrice = t.find('./transactionAmounts/transactionPricePerShare/value').text
        expirationDate = t.find('./expirationDate/value').text
        print(securityTitle, transactionDate, exercisePrice, exerciseShares, expirationDate)
        l.append(transactionDate)

    print(l)
    exit()

    # Write df to CSV
    df.to_csv('.\data\data.csv', mode= 'a', index = False, encoding="utf-8", sep='|')

    # print df 
    print(df)

def download_xml(url, tries=1):
    try:
        response = urllib.request.urlopen(url)
    except:
        print('Something went wrong. Try again', tries)
        if tries < 5:
            time.sleep(5 * tries)
            download_xml(url, tries + 1)
    else:
        # decode the response into a string
        data = response.read().decode('utf-8')
        # set up the regular expression extractoer in order to get the relevant part of the filing
        matcher = re.compile('<\?xml.*ownershipDocument>', flags=re.MULTILINE | re.DOTALL)
        matches = matcher.search(data)
        # the first matching group is the extracted XML of interest
        xml = matches.group(0)
        # instantiate the XML object
        root = ET.fromstring(xml)
        return root

def calculate_transaction_amount (xml):
    """Example function with PEP 484 type annotations.

    Args:
        xml: xml object

    Returns:
        The return value. True for success, False otherwise.

    """
    total = 0
    
    if xml is None:
        return total
    
    nonDerivativeTransactions = xml.findall("./nonDerivativeTable/derivativeTransaction")

    for t in nonDerivativeTransactions:
        # D for disposed or A for acquired
        action = t.find('./transactionAmounts/transactionAcquiredDisposedCode/value').text
        # number of shares disposed/acquired
        shares = t.find('./transactionAmounts/transactionShares/value').text
        # price
        priceRaw = t.find('./transactionAmounts/transactionPricePerShare/value')
        price = 0 if priceRaw is None else priceRaw.text
        # set prefix to -1 if derivatives were disposed. set prefix to 1 if derivates were acquired.
        prefix = -1 if action == 'D' else 1
        # calculate transaction amount in $
        amount = prefix * float(shares) * float(price)
        total += amount
    
    return round(total, 2)


if __name__ == "__main__":
    main()
