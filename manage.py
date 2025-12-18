#!/usr/bin/env python
import os
import sys
import dotenv  # <--- 1. Thêm dòng này

def main():
    # <--- 2. Thêm dòng này để load file .env ngay lập tức
    dotenv.load_dotenv() 

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()