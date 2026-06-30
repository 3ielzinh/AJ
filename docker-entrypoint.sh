#!/bin/bash
set -e

# Aguardar banco de dados ficar pronto (se usar PostgreSQL)
if [ "$DATABASE" = "postgres" ]; then
    echo "Aguardando PostgreSQL..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL disponível."
fi

# Executar migrations
echo "Executando migrations..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Carregar dados iniciais (opcional, apenas em dev)
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.development" ]; then
    echo "Carregando dados iniciais..."
    python manage.py loaddata fixtures/initial_data.json || true
fi

# Executar comando passado
exec "$@"
