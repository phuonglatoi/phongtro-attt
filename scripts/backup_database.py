#!/usr/bin/env python
# ============================================
# scripts/backup_database.py
# Backup SQL Server Database tự động
# ============================================
import os
import sys
import pyodbc
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Class quản lý backup SQL Server Database"""
    
    def __init__(self, server, database, username, password, backup_dir='backups'):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.backup_dir = backup_dir
        
        # Tạo thư mục backup nếu chưa có
        os.makedirs(backup_dir, exist_ok=True)
    
    def get_connection_string(self):
        """Tạo connection string"""
        return (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;TrustServerCertificate=no'
        )
    
    def backup(self):
        """
        Thực hiện backup database
        Returns: (success: bool, backup_file: str, message: str)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{self.database}_backup_{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Đường dẫn trên SQL Server (có thể khác với local path)
        # Nếu backup trên Azure SQL, cần dùng URL hoặc Azure Blob Storage
        server_backup_path = backup_path.replace('\\', '/')
        
        logger.info(f"Starting backup of database '{self.database}'...")
        logger.info(f"Backup file: {backup_filename}")
        
        try:
            conn = pyodbc.connect(self.get_connection_string(), autocommit=True)
            cursor = conn.cursor()
            
            # SQL Server backup command
            backup_sql = f"""
            BACKUP DATABASE [{self.database}]
            TO DISK = N'{server_backup_path}'
            WITH FORMAT,
                 MEDIANAME = 'SQLServerBackups',
                 NAME = 'Full Backup of {self.database}',
                 COMPRESSION,
                 STATS = 10;
            """
            
            logger.info("Executing backup command...")
            cursor.execute(backup_sql)
            
            # Wait for completion
            while cursor.nextset():
                pass
            
            cursor.close()
            conn.close()
            
            # Kiểm tra file đã tạo
            if os.path.exists(backup_path):
                file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                logger.info(f"✅ Backup completed successfully!")
                logger.info(f"   File: {backup_filename}")
                logger.info(f"   Size: {file_size:.2f} MB")
                return True, backup_path, "Backup successful"
            else:
                logger.warning("⚠️ Backup command executed but file not found locally")
                return True, server_backup_path, "Backup executed (file on server)"
        
        except pyodbc.Error as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(f"❌ Backup failed: {error_msg}")
            return False, None, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Backup failed: {error_msg}")
            return False, None, error_msg
    
    def cleanup_old_backups(self, keep_days=30):
        """
        Xóa các backup cũ hơn N ngày
        Args:
            keep_days: Số ngày giữ lại backup
        """
        logger.info(f"Cleaning up backups older than {keep_days} days...")
        
        now = datetime.now()
        deleted_count = 0
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.bak'):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age_days = (now - file_time).days
                    
                    if age_days > keep_days:
                        os.remove(filepath)
                        logger.info(f"   Deleted: {filename} (age: {age_days} days)")
                        deleted_count += 1
            
            logger.info(f"✅ Cleanup completed. Deleted {deleted_count} old backup(s)")
            return deleted_count
        
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            return 0


def main():
    """Main function"""
    # Load từ environment variables hoặc .env
    from dotenv import load_dotenv
    load_dotenv()
    
    server = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_NAME', 'PhongTroATTT')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    
    # Tạo backup
    backup_manager = DatabaseBackup(server, database, username, password)
    success, backup_file, message = backup_manager.backup()
    
    if success:
        # Cleanup old backups
        backup_manager.cleanup_old_backups(keep_days=30)
        logger.info("=" * 60)
        logger.info("BACKUP PROCESS COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("BACKUP PROCESS FAILED")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()

