import json
import pandas as pd
pd.options.mode.chained_assignment = None  # supress copy warning
import numpy as np
import urllib.request
from xml_parser import XmlParser
import xml.etree.cElementTree as ET
import re
import time


def main():


    # Temp Removed to Reduce API calls
    # # Open config file containing private token
    # with open('.\config\credentials.json') as f:
    #     credentials = json.load(f)
    # # API Key
    # TOKEN =  credentials["credentials"]["key"]
    # # API Endpoint
    # API = 'https://api.sec-api.io?token=' + TOKEN

    # # Create filter parameters to send to the API 
    # filter = "formType:\"4\" AND ticker:(NOT \"\") AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[2020-08-05 TO 2020-08-05]"
    # payload = {
    # "query": { "query_string": { "query": filter } },
    # "from": "0",
    # "size": "200",
    # "sort": [{ "filedAt": { "order": "desc" } }]
    # }

    # # Format payload to JSON bytes
    # jsondata = json.dumps(payload)
    # jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes

    # # Send request 
    # req = urllib.request.Request(API)

    # # set the correct HTTP header: Content-Type = application/json
    # req.add_header('Content-Type', 'application/json; charset=utf-8')
    # # set the correct length of your request
    # req.add_header('Content-Length', len(jsondataasbytes))

    # # send the request to the API
    # response = urllib.request.urlopen(req, jsondataasbytes)

    # # read the response 
    # res_body = response.read()
    # # transform the response into JSON
    # filings = json.loads(res_body.decode("utf-8"))

    # # write json response to file.
    # with open('.\data\data.json', 'w') as f:
    #     json.dump(filings, f)


    # Use saved JSON
    with open('.\\data\\data.json', 'r') as f:
    # with open('..\data\data.json', 'r') as f:
        filings = json.load(f)

    # Load results to DataFrame
    df = pd.DataFrame(filings['filings'])

    df = df[['id', 'ticker','companyName','companyNameLong','formType','linkToTxt','linkToFilingDetails']]
    for newcol in ['rptOwnerName', 'owner', 'securityTitle', 'transactionDate', 'exercisePrice', 'exerciseShares', 'expirationDate', 'transactionValue']:
        df[newcol] = np.nan
    col_order = ['ticker','companyName','securityTitle', 'transactionDate', 'exercisePrice', 'exerciseShares', 'expirationDate', 'transactionValue','rptOwnerName', 'owner', 'linkToTxt','linkToFilingDetails']
    df = df[col_order]
    df2 = df[0:0]
    for i, row in df.iterrows():
        xml = df['linkToTxt'].iloc[i]
        xml_root = download_xml(xml)

        derivativeTransactions = xml_root.findall("./derivativeTable/derivativeTransaction")
        nonDerivativeTransactions = xml_root.findall("./nonDerivativeTable/nonDerivativeTransaction")
        allTransactions = derivativeTransactions + nonDerivativeTransactions
        ctr = 0
        for t in allTransactions:
            # Share info
            securityTitle = read_tag(t, './securityTitle/value')
            transactionDate = read_tag(t, './transactionDate/value')
            exerciseShares = float(read_tag(t, './transactionAmounts/transactionShares/value'))
            
            if 'Option' in securityTitle:
                expirationDate = read_tag(t, './expirationDate/value')
                exercisePrice = float(read_tag(t, './transactionAmounts/transactionPricePerShare/value'))
            else:
                expirationDate = ''
                exercisePrice = 0
            transactionValue = exercisePrice * exerciseShares

            # Ticker
            ticker_element = xml_root.findall("./issuer")[0]
            tradingSymbol = read_tag(ticker_element, "./issuerTradingSymbol", '')

            # Owner Relationship
            owner = xml_root.findall("./reportingOwner")[0]
            rptOwnerName = read_tag(owner, './reportingOwnerId/rptOwnerName')
            isDirector = int(read_tag(owner, './reportingOwnerRelationship/isDirector', 0))
            isOfficer = int(read_tag(owner, './reportingOwnerRelationship/isOfficer', 0))
            isTenOwner = int(read_tag(owner, './reportingOwnerRelationship/isTenPercentOwner', 0))
            isOther = int(read_tag(owner, './reportingOwnerRelationship/isOther', 0))
            if isDirector == 1:
                owner = 'Director'
            elif isOfficer == 1:
                owner = 'Officer'
            elif isTenOwner == 1:
                owner = '10% Owner'
            elif isOther == 1:
                owner = 'Other'
            else:
                owner = 'Unknown'
            
            append_to_new_df(df, df2, i, tradingSymbol, rptOwnerName, owner, securityTitle, transactionDate, exercisePrice, exerciseShares, expirationDate, transactionValue)

    # Write df to CSV
    df2.to_csv('.\data\data.csv', index = False, encoding="utf-8", sep='|')


def append_to_new_df(df1, df2, i, tradingSymbol, rptOwnerName, owner, securityTitle, transactionDate, exercisePrice, exerciseShares, expirationDate, transactionValue):
    ticker = df1['ticker'][i]
    companyName = df1['companyName'][i]
    linkToTxt = df1['linkToTxt'][i]
    linkToFilingDetails = df1['linkToFilingDetails'][i]

    df2.loc[-1] = [tradingSymbol,companyName,securityTitle, transactionDate, exercisePrice, exerciseShares, expirationDate, transactionValue, rptOwnerName, owner, linkToTxt, linkToFilingDetails]
    df2.index = df2.index + 1
    df2 = df2.sort_index()
    
def read_tag(root, path, exc=False):
    try:
        v = root.find(path).text
    except (AttributeError, ValueError) as error:
        v = exc
    if v == 'false':
        v = 0
    elif v == 'true':
        v = 1
    
    return v

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
