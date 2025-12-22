import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=phongtro-server.database.windows.net,1433;'
    'DATABASE=PhongTroATTT;'
    'UID=phontroadmin;'
    'PWD=Kaida01101@;'
    'Encrypt=yes;TrustServerCertificate=no'
)
cursor = conn.cursor()

# List all tables
cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_NAME')
tables = cursor.fetchall()
print('All tables in database:')
for t in tables:
    print(' -', t[0])

conn.close()

