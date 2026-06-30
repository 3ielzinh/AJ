# AJ — Assessoria Jurídica

Sistema interno de monitoramento de demandas da CGPJU.

---

## Requisitos

- Python 3.11+
- Git

---

## Primeira vez em um novo computador

```powershell
# 1. Clonar o repositório
git clone https://github.com/3ielzinh/AJ.git
cd AJ

# 2. Criar e ativar o ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar o arquivo de configuração local
copy .env.example .env
# Abra o .env e preencha a SECRET_KEY com qualquer string longa

# 5. Rodar as migrations
.\venv\Scripts\python.exe manage.py migrate

# 6. Carregar os dados
.\venv\Scripts\python.exe manage.py loaddata fixtures/initial_data.json

# 7. Iniciar o servidor
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py runserver 8001
```

Acesse: http://127.0.0.1:8001/

---

## Sincronizar dados entre computadores

Os dados do banco **não são versionados automaticamente**. Use o fluxo abaixo sempre que quiser levar as alterações de um PC para o outro.

### Antes de sair do PC atual (exportar)

```powershell
# 1. Exportar os dados
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
$env:PYTHONUTF8="1"
.\venv\Scripts\python.exe manage.py dumpdata --indent 2 --output fixtures/initial_data.json

# 2. Commitar código + dados
git add .
git commit -m "chore: sync dados + código"
git push
```

Se preferir em uma linha:

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.development"; $env:PYTHONUTF8="1"; .\venv\Scripts\python.exe manage.py dumpdata --indent 2 --output fixtures/initial_data.json
```

### Ao chegar no outro PC (importar)

```powershell
# 1. Baixar as atualizações
git pull

# 2. Instalar novas dependências (se houver)
pip install -r requirements.txt

# 3. Rodar migrations novas (se houver)
.\venv\Scripts\python.exe manage.py migrate

# 4. Carregar os dados atualizados
.\venv\Scripts\python.exe manage.py loaddata fixtures/initial_data.json

# 5. Iniciar o servidor
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py runserver 8001
```

> **Atenção:** o `loaddata` sobrescreve os dados existentes. Sempre exporte antes de começar a trabalhar e importe ao chegar no outro PC.

---

## Criar superusuário (se necessário)

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

---

## Estrutura do projeto

```
AJ/
├── config/          # Settings (base, development, production)
├── core/            # App principal (home, design system)
├── monitoramento/   # App de monitoramento de demandas
├── templates/       # Templates globais
├── static/          # Arquivos estáticos (CSS, JS)
├── fixtures/        # Dados de desenvolvimento (initial_data.json)
├── .env.example     # Modelo do arquivo de configuração
└── requirements.txt
```

---

## Trazer dados de produção para desenvolvimento

Quando os usuários usarem o sistema em produção, os dados ficam no banco PostgreSQL do servidor.
Para trazer esses dados para o seu ambiente de desenvolvimento (ex: para analisar, corrigir ou ter uma cópia atualizada):

### No servidor de produção

```bash
# Acessar o servidor (via SSH ou terminal do servidor)
cd /caminho/do/projeto

# Exportar os dados do banco de produção
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py dumpdata --indent 2 --output fixtures/prod_snapshot.json

# Commitar e subir
git add fixtures/prod_snapshot.json
git commit -m "chore: snapshot dados producao $(date +%Y-%m-%d)"
git push
```

### No seu PC de desenvolvimento

```powershell
# 1. Baixar o snapshot
git pull

# 2. Carregar os dados de produção no banco local
.\venv\Scripts\python.exe manage.py loaddata fixtures/prod_snapshot.json
```

> **Atenção:** o `loaddata` sobrescreve os dados locais. Faça isso apenas quando quiser substituir seu banco dev pelos dados reais de produção.

> **Dica:** mantenha `fixtures/initial_data.json` para dados de desenvolvimento e use `fixtures/prod_snapshot.json` apenas para snapshots de produção — assim você pode alternar entre os dois quando necessário.

---

## Variáveis de ambiente (.env)

Copie `.env.example` para `.env` e preencha:

| Variável | Descrição | Exemplo |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Módulo de settings ativo | `config.settings.development` |
| `SECRET_KEY` | Chave secreta do Django | string longa e aleatória |
| `DEBUG` | Modo debug | `True` (dev) / `False` (prod) |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

> O `.env` nunca é commitado. Cada máquina tem o seu.
