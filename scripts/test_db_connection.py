#!/usr/bin/env python3
"""
🔍 Test Database Connection
Script để kiểm tra kết nối đến SQL Server từ máy ảo
"""

import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from decouple import config

def test_connection():
    """Test kết nối đến SQL Server"""
    
    print("=" * 60)
    print("🔍 TEST DATABASE CONNECTION")
    print("=" * 60)
    print()
    
    # Đọc config từ .env
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='1433')
    db_name = config('DB_NAME', default='QuanLyChoThuePhongTro')
    db_user = config('DB_USER', default='')
    db_password = config('DB_PASSWORD', default='')
    
    print("📋 Thông tin kết nối:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    print(f"  Password: {'*' * len(db_password) if db_password else '(Windows Auth)'}")
    print()
    
    # Test 1: Import pyodbc
    print("🔧 Test 1: Import pyodbc...")
    try:
        import pyodbc
        print("  ✅ pyodbc imported successfully")
    except ImportError as e:
        print(f"  ❌ Error: {e}")
        print("  💡 Cài đặt: pip install pyodbc")
        return False
    
    # Test 2: Check ODBC Driver
    print()
    print("🔧 Test 2: Check ODBC Driver...")
    drivers = [x for x in pyodbc.drivers() if 'SQL Server' in x]
    if drivers:
        print(f"  ✅ Found drivers: {', '.join(drivers)}")
    else:
        print("  ❌ No SQL Server ODBC driver found")
        print("  💡 Cài đặt ODBC Driver 18 for SQL Server")
        return False
    
    # Test 3: Build connection string
    print()
    print("🔧 Test 3: Build connection string...")
    
    if db_user and db_password:
        conn_str = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={db_host},{db_port};'
            f'DATABASE={db_name};'
            f'UID={db_user};'
            f'PWD={db_password};'
            f'TrustServerCertificate=yes;'
        )
        print("  ✅ Using SQL Authentication")
    else:
        conn_str = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={db_host},{db_port};'
            f'DATABASE={db_name};'
            f'Trusted_Connection=yes;'
            f'TrustServerCertificate=yes;'
        )
        print("  ✅ Using Windows Authentication")
    
    # Test 4: Connect to database
    print()
    print("🔧 Test 4: Connect to database...")
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        print("  ✅ Connection successful!")
        
        # Test 5: Execute query
        print()
        print("🔧 Test 5: Execute test query...")
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"  ✅ SQL Server Version:")
        print(f"     {version.split('\\n')[0]}")
        
        # Test 6: Check tables
        print()
        print("🔧 Test 6: Check tables...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        table_count = cursor.fetchone()[0]
        print(f"  ✅ Found {table_count} tables in database")
        
        # Test 7: Check Django tables
        print()
        print("🔧 Test 7: Check Django tables...")
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME LIKE 'django_%'
            ORDER BY TABLE_NAME
        """)
        django_tables = [row[0] for row in cursor.fetchall()]
        if django_tables:
            print(f"  ✅ Found {len(django_tables)} Django tables:")
            for table in django_tables[:5]:  # Show first 5
                print(f"     - {table}")
            if len(django_tables) > 5:
                print(f"     ... and {len(django_tables) - 5} more")
        else:
            print("  ⚠️  No Django tables found (run migrations?)")
        
        conn.close()
        
        # Success summary
        print()
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("🎉 Kết nối database hoạt động tốt!")
        print()
        print("📝 Bước tiếp theo:")
        print("  1. python manage.py migrate")
        print("  2. python manage.py createsuperuser")
        print("  3. python manage.py runserver 0.0.0.0:8000")
        print()
        
        return True
        
    except pyodbc.Error as e:
        print(f"  ❌ Connection failed!")
        print(f"  Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("  1. Kiểm tra SQL Server đã chạy chưa")
        print("  2. Kiểm tra firewall có mở port 1433 không")
        print("  3. Kiểm tra thông tin trong file .env")
        print("  4. Nếu dùng SSH tunnel, kiểm tra tunnel đã chạy chưa:")
        print("     ps aux | grep ssh")
        print()
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

