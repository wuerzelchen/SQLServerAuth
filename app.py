from flask import Flask
import pyodbc
from azure.identity import DefaultAzureCredential
import struct
import os

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

# get the server name from the environment variable (e.g. 'samplesqltest.database.windows.net')
SQL_SERVER = os.environ['SQL_SERVER_NAME']
# get the database name from the environment variable (e.g. 'sample')
SQL_DATABASE = os.environ['SQL_DATABASE_NAME']
SQL_DRIVER = '{ODBC Driver 18 for SQL Server}'

@app.route('/')
def home():
    return 'Welcome to the Flask Entra ID Authentication App'

# initialize the database and check if the user table exists, if not create it. Insert some sample data
@app.route('/init')
def init():
    token = get_access_token()
    conn = get_sql_connection(token)
    cursor = conn.cursor()
    cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' and xtype='U') CREATE TABLE Users (id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(50), email NVARCHAR(50))")
    cursor.execute("INSERT INTO Users (name, email) VALUES ('John Doe', 'john@doe.de')")
    cursor.execute("INSERT INTO Users (name, email) VALUES ('Jane Doe', 'jane@doe.de')")
    conn.commit()
    return 'Database initialized'

# get the data from the database
@app.route('/data')
def data():
    token = get_access_token()
    conn = get_sql_connection(token)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 10 * FROM Users")
    rows = cursor.fetchall()
    return str(rows)

# get the access token from the Azure Identity library
def get_access_token():
    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/.default").token
    
    # convert the token to the format required by pyodbc
    token_bytes = token.encode('UTF-16LE')
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    return token_struct

def get_sql_connection(token):
    conn_str = f"DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    conn = pyodbc.connect(conn_str, attrs_before={1256: token})
    return conn

if __name__ == '__main__':
    app.run(debug=True)