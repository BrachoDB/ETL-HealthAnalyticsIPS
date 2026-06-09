#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Soporte del nuevo layout: apuntar a backend/config y backend/apps
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(BASE_DIR, 'backend')
    backend_apps_dir = os.path.join(backend_dir, 'apps')

    # Permite que Django encuentre apps como top-level: authentication, etl, etc.
    if backend_apps_dir not in sys.path:
        sys.path.insert(0, backend_apps_dir)
    # Permite importar el nuevo paquete de settings/urls
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.healthcare_etl_platform.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
