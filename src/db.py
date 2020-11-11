import pyodbc
import sqlalchemy as sa


engine = sa.create_engine(r'mssql+pyodbc://PC\SQLEXPRESS/insider_screener?driver=SQL+Server+Native+Client+11.0')

conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    r"Server=PC\SQLEXPRESS;"
    "Database=insider_screener;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()
cursor.close()
conn.close()


def read(conn):
    print('read')
    cursor = conn.cursor()
    cursor.execute("select * from filings")
    for row in cursor:
        print(f'{row}')


def write_to_table(df):
    cursor.execute('DROP TABLE IF EXISTS filings')
    print('table dropped. writing to filings')
    df.to_sql("filings", engine)
