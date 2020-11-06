import json
import pandas as pd
import numpy as np
import urllib.request
import xml.etree.cElementTree as ET
import time
import re
import sys
pd.options.mode.chained_assignment = None  # supress copy warning

with open(r'..\config\config.json') as f:
    config = json.load(f)


def read_sec4_to_dataframe(df, df2):
    for i, row in df.iterrows():
        xml = df['linkToTxt'].iloc[i]
        xml_root = download_xml(xml)

        derivativeTransactions = xml_root.findall("./derivativeTable/derivativeTransaction")
        nonDerivativeTransactions = xml_root.findall("./nonDerivativeTable/nonDerivativeTransaction")
        allTransactions = derivativeTransactions + nonDerivativeTransactions

        for t in allTransactions:
            securityTitle = read_tag(t, './securityTitle/value')
            transactionDate = read_tag(t, './transactionDate/value')
            exerciseShares = float(read_tag(t, './transactionAmounts/transactionShares/value'))
            expirationDate = read_tag(t, './expirationDate/value')
            exercisePrice = float(read_tag(t, './transactionAmounts/transactionPricePerShare/value'))
            boughtSold = read_tag(t, './transactionAmounts/transactionAcquiredDisposedCode/value')
            transactionValue = exercisePrice * exerciseShares
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

            append_to_new_df(df, df2, i, tradingSymbol, rptOwnerName, owner, securityTitle,
                             transactionDate, boughtSold, exercisePrice, exerciseShares, expirationDate, transactionValue)


def append_to_new_df(df1, df2, i, tradingSymbol, rptOwnerName, owner, securityTitle, transactionDate, boughtSold, exercisePrice, exerciseShares, expirationDate, transactionValue):
    companyName = df1['companyName'][i]
    linkToTxt = df1['linkToTxt'][i]
    linkToFilingDetails = df1['linkToFilingDetails'][i]

    df2.loc[-1] = [tradingSymbol, companyName, securityTitle, transactionDate, boughtSold, exercisePrice,
                   exerciseShares, expirationDate, transactionValue, rptOwnerName, owner, linkToTxt, linkToFilingDetails]
    df2.index = df2.index + 1
    df2 = df2.sort_index()


def read_tag(root, path, exc=np.nan):
    try:
        v = root.find(path).text
    except (AttributeError, ValueError) as error:
        v = exc
        print(error)
    if v == 'false':
        v = 0
    elif v == 'true':
        v = 1

    return v


def filter_has_ticker(df):
    """Remove rows from the DataFrame that don't have ticker

    Args:
        df: a DataFrame object
    """
    df = df[df['ticker'].str.len() > 1]
    df.reset_index(drop=True, inplace=True)
    return df


def get_only_bought(df2):
    """Takes a dataframe and filters only records where the only trades were buys

    Args:
        df: a DataFrame object

    Returns
        Returns the same dataframe less the filings continaing both buys and sells or only sells
    """
    df = df2.groupby(['ticker', 'transactionDate'], as_index=False)['boughtSold'].apply(''.join).reset_index(name='buysAndSells')
    df['onlyBought'] = np.where(df['buysAndSells'].str.contains('D'), False, True)
    df = df[df['onlyBought']]

    df2 = pd.merge(df2, df, how='right', left_on=['ticker', 'transactionDate'], right_on=['ticker', 'transactionDate'])
    print(df2.shape)
    return df2


def download_xml(url, tries=1):
    try:
        response = urllib.request.urlopen(url)
    except:
        print('Something went wrong. Try again. ', sys.exc_info()[0])
        if tries < 5:
            time.sleep(5 * tries)
            download_xml(url, tries + 1)
    else:
        # decode the response into a string
        data = response.read().decode('utf-8')
        # set up the regular expression extractoer in order to get the relevant part of the filing
        matcher = re.compile(r'<\?xml.*ownershipDocument>',
                             flags=re.MULTILINE | re.DOTALL)
        matches = matcher.search(data)
        # the first matching group is the extracted XML of interest
        xml = matches.group(0)
        # instantiate the XML object
        root = ET.fromstring(xml)
        return root


def calculate_transaction_amount(xml):
    """Example function with PEP 484 type annotations.

    Args:
        xml: xml object

    Returns:
        The return value. True for success, False otherwise.

    """
    total = 0

    if xml is None:
        return total

    nonDerivativeTransactions = xml.findall(
        "./nonDerivativeTable/derivativeTransaction")

    for t in nonDerivativeTransactions:
        # D for disposed or A for acquired
        action = t.find(
            './transactionAmounts/transactionAcquiredDisposedCode/value').text
        # number of shares disposed/acquired
        shares = t.find('./transactionAmounts/transactionShares/value').text
        # price
        priceRaw = t.find(
            './transactionAmounts/transactionPricePerShare/value')
        price = 0 if priceRaw is None else priceRaw.text
        # set prefix to -1 if derivatives were disposed. set prefix to 1 if derivates were acquired.
        prefix = -1 if action == 'D' else 1
        # calculate transaction amount in $
        amount = prefix * float(shares) * float(price)
        total += amount

    return round(total, 2)
