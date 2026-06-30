# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python em um venv
COPY requirements.txt .
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip setuptools && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv do builder
COPY --from=builder /app/venv /app/venv

# Copiar código da aplicação
COPY . .

# Copiar entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Variáveis de ambiente
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media

# Usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
