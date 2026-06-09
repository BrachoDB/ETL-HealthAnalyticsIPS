# Manual de instalación

## 1. Requisitos
- Python 3.10+
- PostgreSQL
- pip

## 2. Instalación
### Entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Dependencias
```bash
pip install -r requirements.txt
```

### Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Superusuario
```bash
python manage.py createsuperuser
```

## 3. Ejecutar
```bash
python manage.py runserver
```

## 4. Probar API y Dashboard
- Swagger: `http://127.0.0.1:8000/api/docs/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`

