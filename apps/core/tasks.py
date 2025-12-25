# ============================================
# apps/core/tasks.py
# Celery Background Tasks
# ============================================
import os
import sys
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(name='backup_database_task')
def backup_database_task():
    """
    Celery task để backup database tự động
    Chạy hàng ngày lúc 2:00 AM
    """
    logger.info("=" * 60)
    logger.info("Starting automated database backup...")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        # Import backup module
        sys.path.insert(0, os.path.join(settings.BASE_DIR, 'scripts'))
        
        # Kiểm tra xem đang dùng Azure SQL hay SQL Server thông thường
        db_host = os.getenv('DB_HOST', '')
        
        if 'database.windows.net' in db_host:
            # Azure SQL Database
            from backup_azure_sql import AzureSQLBackup
            
            server = os.getenv('DB_HOST')
            database = os.getenv('DB_NAME')
            username = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            
            backup_manager = AzureSQLBackup(server, database, username, password)
            success, backup_name, message = backup_manager.create_database_copy()
            
            if success:
                # Cleanup old backups
                backup_manager.delete_old_backups(keep_count=7)
                logger.info(f"✅ Azure SQL backup completed: {backup_name}")
                return {'status': 'success', 'backup': backup_name, 'message': message}
            else:
                logger.error(f"❌ Azure SQL backup failed: {message}")
                return {'status': 'error', 'message': message}
        
        else:
            # SQL Server thông thường
            from backup_database import DatabaseBackup
            
            server = os.getenv('DB_HOST', 'localhost')
            database = os.getenv('DB_NAME', 'PhongTroATTT')
            username = os.getenv('DB_USER', 'sa')
            password = os.getenv('DB_PASSWORD', '')
            
            backup_manager = DatabaseBackup(server, database, username, password)
            success, backup_file, message = backup_manager.backup()
            
            if success:
                # Cleanup old backups
                backup_manager.cleanup_old_backups(keep_days=30)
                logger.info(f"✅ SQL Server backup completed: {backup_file}")
                return {'status': 'success', 'backup': backup_file, 'message': message}
            else:
                logger.error(f"❌ SQL Server backup failed: {message}")
                return {'status': 'error', 'message': message}
    
    except Exception as e:
        error_msg = f"Backup task failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {'status': 'error', 'message': error_msg}


@shared_task(name='cleanup_old_logs_task')
def cleanup_old_logs_task():
    """
    Celery task để dọn dẹp log cũ
    Chạy hàng ngày lúc 3:00 AM
    """
    logger.info("Starting log cleanup task...")
    
    try:
        from apps.accounts.models import SecurityLogs, FailedLoginAttempts, AuditLogs
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        # Xóa failed login attempts > 7 ngày
        failed_login_cutoff = now - timedelta(days=7)
        deleted_failed = FailedLoginAttempts.objects.filter(
            attempted_at__lt=failed_login_cutoff
        ).delete()[0]
        
        # Xóa security logs > 180 ngày
        security_cutoff = now - timedelta(days=180)
        deleted_security = SecurityLogs.objects.filter(
            created_at__lt=security_cutoff
        ).delete()[0]
        
        # Xóa audit logs > 180 ngày
        audit_cutoff = now - timedelta(days=180)
        deleted_audit = AuditLogs.objects.filter(
            created_at__lt=audit_cutoff
        ).delete()[0]
        
        logger.info(f"✅ Log cleanup completed:")
        logger.info(f"   - Failed login attempts: {deleted_failed}")
        logger.info(f"   - Security logs: {deleted_security}")
        logger.info(f"   - Audit logs: {deleted_audit}")
        
        return {
            'status': 'success',
            'deleted': {
                'failed_logins': deleted_failed,
                'security_logs': deleted_security,
                'audit_logs': deleted_audit
            }
        }
    
    except Exception as e:
        error_msg = f"Log cleanup failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {'status': 'error', 'message': error_msg}


@shared_task(name='check_database_health_task')
def check_database_health_task():
    """
    Kiểm tra sức khỏe database
    Chạy mỗi giờ
    """
    logger.info("Checking database health...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Kiểm tra kết nối
            cursor.execute("SELECT 1")
            
            # Kiểm tra kích thước database (SQL Server)
            cursor.execute("""
                SELECT 
                    DB_NAME() as DatabaseName,
                    SUM(size * 8 / 1024) as SizeMB
                FROM sys.master_files
                WHERE database_id = DB_ID()
            """)
            
            result = cursor.fetchone()
            db_name = result[0]
            db_size_mb = result[1]
            
            logger.info(f"✅ Database health check passed")
            logger.info(f"   Database: {db_name}")
            logger.info(f"   Size: {db_size_mb} MB")
            
            return {
                'status': 'healthy',
                'database': db_name,
                'size_mb': db_size_mb
            }
    
    except Exception as e:
        error_msg = f"Database health check failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {'status': 'unhealthy', 'message': error_msg}

