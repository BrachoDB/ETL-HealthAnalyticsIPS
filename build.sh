#!/usr/bin/env bash
# Render.com build script for HealthAnalytics IPS (Django + MySQL/Aiven).
# Exit immediately on any error so a failed step fails the deploy.
set -o errexit

# The Django project lives inside the backend/ directory.
cd backend

# 1. Install Python dependencies.
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect static files (served by WhiteNoise in production).
python manage.py collectstatic --no-input

# 3. Apply database migrations against the external MySQL (Aiven).
python manage.py migrate --no-input
