# Deploy — Desenvolvimento para Produção

Guia completo para publicar o projeto AJ em uma máquina de produção (servidor local/rede).

---

## 1. Preparar a máquina de produção

1. Instale **Python 3.12+** — https://www.python.org/downloads/
2. Instale **PostgreSQL 15+** — https://www.postgresql.org/download/
3. Instale **Git** — https://git-scm.com/
4. Crie a pasta do sistema, por exemplo: `C:\sistemas\AJ`

---

## 2. Criar o banco de dados (PostgreSQL)

Abra o terminal do PostgreSQL (`psql`) como administrador:

```sql
CREATE DATABASE aj;
CREATE USER aj_user WITH PASSWORD 'senha-forte-aqui';
GRANT ALL PRIVILEGES ON DATABASE aj TO aj_user;
```

---

## 3. Publicar o código

No ambiente de desenvolvimento, envie para o repositório remoto:

```powershell
git add .
git commit -m "versao X"
git push origin main
```

Na máquina de produção, clone ou atualize:

```powershell
# Primeira vez
git clone <URL_DO_REPOSITORIO> C:\sistemas\AJ
cd C:\sistemas\AJ

# Atualizações posteriores
git pull origin main
```

---

## 4. Criar ambiente virtual e instalar dependências

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Configurar variáveis de ambiente

```powershell
copy .env.example .env
notepad .env
```

Ajuste o `.env` para produção:

```ini
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<gere-uma-chave-forte>
DEBUG=False
ALLOWED_HOSTS=<IP_DO_SERVIDOR>,localhost,127.0.0.1

DB_NAME=aj
DB_USER=aj_user
DB_PASSWORD=senha-forte-aqui
DB_HOST=localhost
DB_PORT=5432

CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

**Gerar SECRET_KEY:**
```powershell
.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Aplicar migrações

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
.\venv\Scripts\python.exe manage.py migrate
```

---

## 7. Criar superusuário (primeira vez)

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

---

## 8. Coletar arquivos estáticos

```powershell
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

---

## 9. Iniciar o servidor

Clique duplo no arquivo `INICIAR SERVIDOR.bat` ou execute:

```powershell
.\scripts\start_prod.ps1
```

O sistema estará disponível em:
- Esta máquina: `http://localhost:8080`
- Rede local: `http://<IP_DO_SERVIDOR>:8080`

---

## 10. Checklist de validação

- [ ] Acesse `/health/` — deve retornar `{"status": "ok"}`
- [ ] Acesse `/admin/` — login com superusuário funciona
- [ ] Acesse `/design-system/` — CSS e layout carregam corretamente
- [ ] Verifique o banco de dados: operações de leitura e escrita funcionam

---

## 11. Atualizações futuras

```powershell
cd C:\sistemas\AJ
git pull origin main
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
# Reinicie o processo do servidor
```

---

## 12. Boas práticas de segurança

- Nunca versione o arquivo `.env`
- Use uma conta de banco com privilégios mínimos (apenas no banco da aplicação)
- Restrinja o firewall: libere apenas a porta do servidor (ex.: 8080) para a rede interna
- Mantenha backups periódicos do PostgreSQL:
  ```powershell
  pg_dump -U aj_user aj > backup_aj_$(Get-Date -Format 'yyyyMMdd').sql
  ```
- Ative HTTPS com proxy reverso (nginx/Caddy) quando possível
