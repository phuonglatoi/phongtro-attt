#!/usr/bin/env python
# ============================================
# scripts/backup_azure_sql.py
# Backup Azure SQL Database (Export to BACPAC)
# ============================================
import os
import sys
import pyodbc
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureSQLBackup:
    """
    Backup Azure SQL Database
    
    Note: Azure SQL Database không hỗ trợ BACKUP TO DISK như SQL Server thông thường.
    Có 3 cách backup Azure SQL:
    1. Automatic backups (Azure tự động) - ĐÃ CÓ SẴN
    2. Export to BACPAC file (manual)
    3. Copy database to another server
    
    Script này sẽ tạo database copy để backup
    """
    
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
    
    def get_connection_string(self):
        """Tạo connection string"""
        return (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE=master;'  # Connect to master for database operations
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;TrustServerCertificate=no'
        )
    
    def create_database_copy(self):
        """
        Tạo bản copy của database (Azure SQL Database Copy)
        Đây là cách backup tốt nhất cho Azure SQL
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_db_name = f"{self.database}_backup_{timestamp}"
        
        logger.info(f"Creating database copy: {backup_db_name}")
        
        try:
            conn = pyodbc.connect(self.get_connection_string(), autocommit=True)
            cursor = conn.cursor()
            
            # Create database copy
            copy_sql = f"""
            CREATE DATABASE [{backup_db_name}]
            AS COPY OF [{self.database}];
            """
            
            logger.info("Executing database copy command...")
            cursor.execute(copy_sql)
            
            logger.info("✅ Database copy initiated successfully!")
            logger.info(f"   Backup database: {backup_db_name}")
            logger.info("   Note: Copy process may take several minutes to complete.")
            logger.info("   Check Azure Portal for progress.")
            
            cursor.close()
            conn.close()
            
            return True, backup_db_name, "Database copy initiated"
        
        except pyodbc.Error as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(f"❌ Backup failed: {error_msg}")
            return False, None, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Backup failed: {error_msg}")
            return False, None, error_msg
    
    def list_backup_databases(self):
        """Liệt kê các database backup"""
        try:
            conn = pyodbc.connect(self.get_connection_string())
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, create_date, 
                       CAST(DATABASEPROPERTYEX(name, 'Status') AS VARCHAR(20)) as status
                FROM sys.databases
                WHERE name LIKE '%_backup_%'
                ORDER BY create_date DESC
            """)
            
            backups = cursor.fetchall()
            
            logger.info(f"\nFound {len(backups)} backup database(s):")
            for backup in backups:
                logger.info(f"  - {backup[0]} (Created: {backup[1]}, Status: {backup[2]})")
            
            cursor.close()
            conn.close()
            
            return backups
        
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    def delete_old_backups(self, keep_count=7):
        """
        Xóa các database backup cũ, chỉ giữ lại N bản mới nhất
        Args:
            keep_count: Số lượng backup giữ lại
        """
        logger.info(f"Cleaning up old backups (keeping {keep_count} most recent)...")
        
        try:
            conn = pyodbc.connect(self.get_connection_string(), autocommit=True)
            cursor = conn.cursor()
            
            # Get list of backup databases
            cursor.execute("""
                SELECT name, create_date
                FROM sys.databases
                WHERE name LIKE '%_backup_%'
                ORDER BY create_date DESC
            """)
            
            backups = cursor.fetchall()
            
            if len(backups) <= keep_count:
                logger.info(f"   Only {len(backups)} backup(s) found. No cleanup needed.")
                return 0
            
            # Delete old backups
            deleted_count = 0
            for backup in backups[keep_count:]:
                db_name = backup[0]
                try:
                    logger.info(f"   Deleting: {db_name}")
                    cursor.execute(f"DROP DATABASE [{db_name}]")
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"   Failed to delete {db_name}: {str(e)}")
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Cleanup completed. Deleted {deleted_count} old backup(s)")
            return deleted_count
        
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            return 0


def main():
    """Main function"""
    from dotenv import load_dotenv
    load_dotenv()
    
    server = os.getenv('DB_HOST', 'phongtro-server.database.windows.net')
    database = os.getenv('DB_NAME', 'PhongTroATTT')
    username = os.getenv('DB_USER', 'phontroadmin')
    password = os.getenv('DB_PASSWORD', '')
    
    logger.info("=" * 60)
    logger.info("AZURE SQL DATABASE BACKUP")
    logger.info("=" * 60)
    
    backup_manager = AzureSQLBackup(server, database, username, password)
    
    # Create backup
    success, backup_name, message = backup_manager.create_database_copy()
    
    if success:
        # List all backups
        backup_manager.list_backup_databases()
        
        # Cleanup old backups (keep 7 most recent)
        backup_manager.delete_old_backups(keep_count=7)
        
        logger.info("=" * 60)
        logger.info("BACKUP PROCESS COMPLETED")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("BACKUP PROCESS FAILED")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()

