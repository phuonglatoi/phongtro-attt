#!/usr/bin/env python
# ============================================
# scripts/restore_database.py
# Restore SQL Server Database từ backup
# ============================================
import os
import sys
import pyodbc
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseRestore:
    """Class quản lý restore SQL Server Database"""
    
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
    
    def get_connection_string(self, db='master'):
        """Tạo connection string"""
        return (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={db};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;TrustServerCertificate=no'
        )
    
    def list_backups(self, backup_dir='backups'):
        """Liệt kê các file backup có sẵn"""
        if not os.path.exists(backup_dir):
            logger.warning(f"Backup directory not found: {backup_dir}")
            return []
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.bak'):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'created': file_time,
                    'size_mb': file_size
                })
        
        # Sort by created time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def restore(self, backup_file, target_database=None):
        """
        Restore database từ file backup
        
        Args:
            backup_file: Đường dẫn file .bak
            target_database: Tên database đích (nếu None, dùng tên gốc)
        
        Returns:
            (success: bool, message: str)
        """
        if target_database is None:
            target_database = self.database
        
        logger.info("=" * 60)
        logger.info("DATABASE RESTORE")
        logger.info("=" * 60)
        logger.info(f"Backup file: {backup_file}")
        logger.info(f"Target database: {target_database}")
        
        if not os.path.exists(backup_file):
            error_msg = f"Backup file not found: {backup_file}"
            logger.error(error_msg)
            return False, error_msg
        
        try:
            # Connect to master database
            conn = pyodbc.connect(self.get_connection_string('master'), autocommit=True)
            cursor = conn.cursor()
            
            # Step 1: Set database to single user mode (disconnect all users)
            logger.info("Step 1: Disconnecting all users...")
            try:
                cursor.execute(f"""
                    ALTER DATABASE [{target_database}]
                    SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                """)
                logger.info("   ✅ Database set to single user mode")
            except pyodbc.Error as e:
                logger.warning(f"   ⚠️ Could not set single user mode: {str(e)}")
            
            # Step 2: Restore database
            logger.info("Step 2: Restoring database...")
            
            restore_sql = f"""
            RESTORE DATABASE [{target_database}]
            FROM DISK = N'{backup_file}'
            WITH REPLACE,
                 STATS = 10;
            """
            
            cursor.execute(restore_sql)
            
            # Wait for completion
            while cursor.nextset():
                pass
            
            logger.info("   ✅ Database restored successfully")
            
            # Step 3: Set database back to multi user mode
            logger.info("Step 3: Setting database to multi user mode...")
            cursor.execute(f"""
                ALTER DATABASE [{target_database}]
                SET MULTI_USER;
            """)
            logger.info("   ✅ Database set to multi user mode")
            
            cursor.close()
            conn.close()
            
            logger.info("=" * 60)
            logger.info("✅ RESTORE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            return True, "Restore successful"
        
        except pyodbc.Error as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(f"❌ Restore failed: {error_msg}")
            
            # Try to set back to multi user mode
            try:
                cursor.execute(f"ALTER DATABASE [{target_database}] SET MULTI_USER;")
            except:
                pass
            
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Restore failed: {error_msg}")
            return False, error_msg


def main():
    """Main function"""
    from dotenv import load_dotenv
    load_dotenv()
    
    server = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_NAME', 'PhongTroATTT')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    
    restore_manager = DatabaseRestore(server, database, username, password)
    
    # List available backups
    logger.info("Available backups:")
    backups = restore_manager.list_backups()
    
    if not backups:
        logger.error("No backup files found!")
        sys.exit(1)
    
    for i, backup in enumerate(backups, 1):
        logger.info(f"{i}. {backup['filename']}")
        logger.info(f"   Created: {backup['created']}")
        logger.info(f"   Size: {backup['size_mb']:.2f} MB")
    
    # Interactive mode: choose backup to restore
    if len(sys.argv) > 1:
        # Command line argument: backup file path
        backup_file = sys.argv[1]
    else:
        # Use most recent backup
        backup_file = backups[0]['filepath']
        logger.info(f"\nUsing most recent backup: {backups[0]['filename']}")
    
    # Confirm before restore
    logger.warning("\n⚠️  WARNING: This will OVERWRITE the current database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        logger.info("Restore cancelled by user")
        sys.exit(0)
    
    # Perform restore
    success, message = restore_manager.restore(backup_file)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

