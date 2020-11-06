import pyodbc
import sqlalchemy as sa


engine = sa.create_engine(r'mssql+pyodbc://PC\SQLEXPRESS/sec4?driver=SQL+Server+Native+Client+11.0')

conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    r"Server=PC\SQLEXPRESS;"
    "Database=sec4;"
    "Trusted_Connection=yes;"
)


def read(conn):
    print('read')
    cursor = conn.cursor()
    cursor.execute("select * from filings")
    for row in cursor:
        print(f'{row}')


def write_to_table(df):
    df.to_sql("sec4", engine)
