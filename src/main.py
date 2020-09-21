import json
import sec4_reader as reader
import sec_api as sa
import pandas as pd
pd.options.mode.chained_assignment = None  # supress copy warning
import numpy as np
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
    # filings = sa.get_filings()
    filings = sa.get_filings_over_period('2020-01-02', '2020-01-03')

    print('generate DataFrame')
    # Load results to DataFrame
    df = pd.DataFrame(filings['filings'])

    # Create DataFrame
    df = df[config['dataframe']['columns_shortlist']]
    # df = df.sort_values(by='filedAt')
    print(df.filedAt)
    exit()

    # Add columns additional columns
    for new_column in config['dataframe']['columns_new']:
        df[new_column] = np.nan

    df = df[config['dataframe']['column_order']]
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
               index=False, encoding='utf-8', sep='|')


if __name__ == '__main__':
    main()
