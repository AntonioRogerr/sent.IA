#!/bin/sh

# O script irá parar a execução se qualquer comando falhar
set -e

# Espera o banco de dados ficar pronto (opcional, mas recomendado)
# Você precisará adicionar 'netcat' ao seu Dockerfile se usar isso
# echo "Waiting for postgres..."
# while ! nc -z db 5432; do
#   sleep 0.1
# done
# echo "PostgreSQL started"

# Aplica as migrações do banco de dados
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000