"""Setup local SQL Server database for development"""
import pyodbc

def main():
    # Connect with Windows Authentication
    conn_str = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=master;'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes'
    )
    
    print("Connecting to SQL Server...")
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    # 1. Create database
    print("Creating database QuanLyChoThuePhongTro...")
    cursor.execute("""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'QuanLyChoThuePhongTro')
        CREATE DATABASE QuanLyChoThuePhongTro
    """)
    print("✅ Database created!")
    
    # 2. Create login
    print("Creating login phongtro_app_user...")
    cursor.execute("""
        IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = N'phongtro_app_user')
        CREATE LOGIN phongtro_app_user WITH PASSWORD = N'StrongP@ssw0rd!2024', DEFAULT_DATABASE = QuanLyChoThuePhongTro
    """)
    print("✅ Login created!")
    
    conn.close()
    
    # 3. Create user in database
    conn_str2 = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=QuanLyChoThuePhongTro;'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes'
    )
    
    conn2 = pyodbc.connect(conn_str2, autocommit=True)
    cursor2 = conn2.cursor()
    
    print("Creating user in database...")
    cursor2.execute("""
        IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = N'phongtro_app_user')
        CREATE USER phongtro_app_user FOR LOGIN phongtro_app_user
    """)
    
    cursor2.execute("ALTER ROLE db_owner ADD MEMBER phongtro_app_user")
    print("✅ User has db_owner role!")
    
    conn2.close()
    
    # 4. Test connection with the new user
    print("\nTesting connection with phongtro_app_user...")
    test_conn_str = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=QuanLyChoThuePhongTro;'
        'UID=phongtro_app_user;'
        'PWD=StrongP@ssw0rd!2024;'
        'TrustServerCertificate=yes'
    )
    
    test_conn = pyodbc.connect(test_conn_str)
    print("✅ Connection successful!")
    test_conn.close()
    
    print("\n🎉 Setup complete! Your .env settings are correct.")

if __name__ == "__main__":
    main()

