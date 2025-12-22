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

# Read and execute the SQL script
with open('scripts/database_setup.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Replace database name for Azure
sql_content = sql_content.replace('USE [QuanLyChoThuePhongTro];', 'USE [PhongTroATTT];')

# Split by GO statements
statements = sql_content.split('GO')

for i, stmt in enumerate(statements):
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--'):
        try:
            cursor.execute(stmt)
            conn.commit()
            print(f'Executed statement {i+1}')
        except Exception as e:
            print(f'Error in statement {i+1}: {e}')
            # Continue with next statement

cursor.close()
conn.close()
print('Done!')

