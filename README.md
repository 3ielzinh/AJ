# AJ — Assessoria Jurídica

Sistema interno de monitoramento de demandas da CGPJU.

---

## Visão Geral

O AJ é um sistema interno em Django voltado para organização, acompanhamento e priorização de demandas da CGPJU, com foco em monitoramento sistêmico, rastreabilidade de processos SEI e leitura operacional do fluxo de trabalho.

Atualmente o projeto reúne três frentes principais:

- Monitoramento sistêmico de demandas com filtros, tabs por categoria, dashboard, reordenação de prioridade e CRUD completo.
- Consulta e consolidação de informações do SEI, incluindo processos, documentos e relação com autoria, edição, análise e assinatura.
- Camada de interface institucional com design system próprio, telas iniciais redesenhadas e experiência mais consistente entre home, perfil e monitoramento.

---

## Principais Fluxos

### Home

- Painel inicial com métricas consolidadas de demandas, taxa de conclusão, distribuição por tipo e atalhos operacionais.

### Perfil

- Visão da conta autenticada.
- Consolidação de participação documental no SEI.
- Filtros por texto, tipo de participação e mês/ano.
- Exportação CSV dos documentos vinculados ao usuário.

### Monitoramento

- Hub principal com entrada para monitoramento sistêmico, monitoramento SEI e área AJ.
- Lista sistêmica com filtros, tabs por categoria e navegação por status.
- Dashboard com KPIs, gráficos e destaque para demandas antigas/em atraso.
- Reordenação de prioridades por categoria com drag and drop.
- Fluxo de criação, edição e exclusão de demandas.

### SEI

- Consulta de processos e documentos com busca ampla.
- Relação entre documento, processo, tipo, assunto e metadados relevantes.

---

## Interface e Design System

O front do projeto foi consolidado em torno de um design system simples, baseado em:

- tokens em `static/css/tokens.css`
- estilos-base em `static/css/base.css`
- componentes compartilhados em `static/css/components.css`
- template de referência em `core/templates/core/design_system.html`

Telas com tratamento visual mais recente:

- Home principal
- Perfil
- Hub de monitoramento
- Lista sistêmica
- Dashboard
- Reordenação de prioridades
- Formulário de nova demanda e edição

Observações importantes:

- A rota `core:design_system` existe para referência visual e fica restrita a usuários com `is_staff`.
- O objetivo do front atual é manter consistência entre páginas operacionais sem depender de bibliotecas visuais externas além do que já existe no projeto.

---

## Skills e Workflow no Workspace

Este repositório passou a incorporar um workflow de iteração visual apoiado por skills instaladas no workspace. Hoje, as mais relevantes para manutenção da interface são:

- `frontend-design`: usada como referência para decisões de layout, hierarquia visual, hero sections, distribuição espacial e refinamento das telas.
- `find-skills`: usada para descoberta e instalação de novas skills de apoio ao fluxo de desenvolvimento.

Essas skills não são dependências de runtime da aplicação. Elas servem apenas como apoio ao processo de desenvolvimento dentro do editor/agente.

Quando evoluir a interface, mantenha este norte:

- reaproveitar `components.css` antes de criar estilos isolados por página
- preservar a linguagem já aplicada em home, monitoramento, perfil, dashboard e formulários
- validar mudanças com `manage.py check` após edições estruturais de template

---

## Rotas Principais

- `/` — home
- `/perfil/` — perfil do usuário
- `/monitoramento/` — hub do monitoramento
- `/monitoramento/sistemico/` — lista sistêmica de demandas
- `/monitoramento/dashboard/` — dashboard do monitoramento
- `/monitoramento/reordenar/` — reordenação de prioridades
- `/monitoramento/nova/` — nova demanda
- `/monitoramento/<pk>/editar/` — edição de demanda
- `/monitoramento/<pk>/excluir/` — exclusão de demanda
- `/monitoramento/sei/` — consulta de processos SEI

---

## Validação Rápida

Após mudanças em templates, estilos ou views, use pelo menos:

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py check
```

---

## Requisitos

### Opção 1: Docker (Recomendado)
- Docker Desktop ou Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### Opção 2: Python Local
- Python 3.11+
- PostgreSQL 12+ (opcional, pode usar SQLite em dev)
- Git

---

## Setup com Docker (Desenvolvimento)

### 1. Clonar repositório
```powershell
git clone https://github.com/3ielzinh/AJ.git
cd AJ
```

### 2. Configurar variáveis de ambiente
```powershell
copy .env.docker.example .env
```

### 3. Iniciar containers
```powershell
docker compose up -d
```

O sistema estará disponível em: **http://localhost:8000**

Banco de dados PostgreSQL em: **localhost:5432**

### 4. Parar containers
```powershell
docker compose down
```

### 5. Ver logs
```powershell
docker compose logs -f web
docker compose logs -f db
```

---

## Setup Local (Desenvolvimento) — sem Docker

```powershell
# 1. Clonar o repositório
git clone https://github.com/3ielzinh/AJ.git
cd AJ

# 2. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
copy .env.example .env

# 5. Rodar as migrations
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py migrate

# 6. Carregar os dados
.\venv\Scripts\python.exe manage.py loaddata fixtures/initial_data.json

# 7. Iniciar o servidor
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py runserver 8001
```

Acesse: http://127.0.0.1:8001/

---

## Sincronizar Dados com Docker

Com Docker, o banco de dados fica persistido em volumes. Para sincronizar entre PCs:

### Exportar dados (na máquina atual)
```powershell
docker compose exec web python manage.py dumpdata --indent 2 --output fixtures/initial_data.json
git add fixtures/initial_data.json
git commit -m "chore: sync dados"
git push
```

### Importar dados (na outra máquina)
```powershell
git pull
docker compose up -d
docker compose exec web python manage.py loaddata fixtures/initial_data.json
```

---

## CI/CD com GitHub Actions

O projeto está configurado para deploy automático com GitHub Actions.

### Setup Inicial (Uma vez por repositório)

1. **Adicionar secrets no GitHub** (Settings → Secrets and variables → Actions):
	- `DOCKER_USERNAME`: seu usuário Docker Hub
	- `DOCKER_PASSWORD`: seu token Docker Hub (não use senha)
	- `PROD_HOST`: IP ou domínio do servidor de produção
	- `PROD_USER`: usuário SSH do servidor
	- `PROD_SSH_KEY`: chave privada SSH (conteúdo de `~/.ssh/id_rsa`)
	- `PROD_SSH_PORT`: porta SSH (padrão 22)
	- `PROD_DOMAIN`: domínio da produção

2. **Fluxo automático**:
	- Ao fazer `git push` para `main` ou `develop`, o workflow é acionado
	- Testes rodam automaticamente
	- Se tudo passar, a imagem é builda e enviada para Docker Hub
	- Se for branch `main`, faz deploy automático no servidor

---

## Sincronizar Dados Local (sem Docker) entre PCs

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

## Deploy Manual em Produção

Se não quiser usar CI/CD automático, você pode fazer deploy manualmente via Docker:

### No servidor de produção

```bash
cd /caminho/do/projeto/AJ

# 1. Atualizar código
git pull origin main

# 2. Atualizar arquivo de ambiente
# Editar .env com variáveis de produção

# 3. Parar containers antigos e iniciar novos
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 4. Rodar migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 5. Coletar arquivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 6. Verificar status
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
```

---

## Criar Superusuário

### Com Docker
```powershell
docker compose exec web python manage.py createsuperuser
```

### Local (sem Docker)

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py createsuperuser
```

---

## Estrutura do Projeto

```
AJ/
├── config/              # Settings (base, development, production)
├── core/                # App principal (home, perfil, design system)
├── monitoramento/       # App de monitoramento de demandas
├── templates/           # Templates globais
├── static/              # Arquivos estáticos (CSS, JS)
├── fixtures/            # Dados de desenvolvimento (initial_data.json)
├── .github/workflows/   # Configuração CI/CD
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração dev
├── docker-compose.prod.yml  # Orquestração produção
├── docker-entrypoint.sh # Script de inicialização
├── .dockerignore        # Arquivos ignorados no Docker
├── .env.docker.example  # Variáveis Docker de exemplo
├── .env.example         # Variáveis locais de exemplo
└── requirements.txt     # Dependências Python
```

---

## Variáveis de Ambiente

### Desenvolvimento (`.env`)
Copie `.env.example` e customize.

### Docker Desenvolvimento (`.env`)
Copie `.env.docker.example` e customize com variáveis do banco PostgreSQL.

### Docker Produção (`.env` no servidor)
Configure com variáveis seguras de produção:
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DEBUG=False`
- `SECRET_KEY=<chave-segura-aleatória>`
- `ALLOWED_HOSTS=seu-dominio.com`
- Credenciais PostgreSQL de produção

---

## Troubleshooting

### Docker não inicia
```powershell
docker system prune -a
docker volume prune
docker compose up -d --build
```

### Porta já em uso
```powershell
# Mudar porta no docker-compose.yml
# De: 8000:8000
# Para: 8001:8000
```

### Banco não conecta
```powershell
docker compose down -v
docker compose up -d
```

### Ver logs detalhados
```powershell
docker compose logs --follow
```

---

## Referências

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## Governanca do Projeto

Este repositorio possui documentos de apoio para agentes e manutencao continua:

- `AGENTS.md`: guia principal de desenvolvimento para agentes e pessoas.
- `CHANGELOG.md`: historico de mudancas relevantes por versao.
- `ROADMAP.md`: direcao planejada para proximas versoes.
- `TODO.md`: pendencias operacionais ainda nao planejadas em detalhe.
- `docs/adr/`: decisoes arquiteturais registradas.
- `.ai/context/`: contexto funcional do produto.
- `.ai/rules/`: regras de trabalho para agentes.
- `.ai/prompts/`: prompts reutilizaveis para tarefas recorrentes.
- `.ai/agents/`: agentes especializados para backend, frontend, review, QA, docs, DBA e DevOps.

---

## Arquitetura

O AJ segue uma arquitetura Django tradicional, com separacao por apps e templates compartilhados.

Fluxo geral de uma requisicao:

```text
Usuario
  |
  v
URL
  |
  v
View
  |
  v
Form / Service / Query
  |
  v
Model
  |
  v
PostgreSQL ou SQLite em desenvolvimento local
  |
  v
Template
  |
  v
HTML + CSS modular
```

Camadas principais:

- `config`: configuracao Django, urls globais, settings, WSGI e ASGI.
- `core`: home, perfil, autenticacao complementar e referencia do design system.
- `monitoramento`: demandas, SEI, dashboard, filtros, prioridades e importacoes.
- `templates`: layouts e componentes reutilizaveis.
- `static/css`: tokens, base visual e componentes compartilhados.
- `fixtures`: dados de apoio para desenvolvimento e sincronizacao.

---

## Apps

### core

Responsavel pelas telas institucionais e transversais:

- home
- perfil do usuario
- design system de referencia
- formularios e views de apoio

### monitoramento

Responsavel pelo dominio operacional:

- demandas
- lista sistemica
- dashboard
- reordenacao de prioridades
- consulta SEI
- comandos de importacao

---

## Fluxos Funcionais

### Fluxo Monitoramento

```text
Usuario
  |
  v
/monitoramento/
  |
  v
Hub de monitoramento
  |
  +--> Lista sistemica
  +--> Dashboard
  +--> Reordenacao
  +--> Nova demanda / editar / excluir
```

### Fluxo SEI

```text
Usuario
  |
  v
/monitoramento/sei/
  |
  v
Busca de processos e documentos
  |
  v
ProcessoSEI / DocumentoSEI
  |
  v
Resultado consolidado por processo, documento, tipo e participacao
```

### Fluxo Dashboard

```text
Demandas
  |
  v
Consultas agregadas
  |
  v
KPIs, graficos e destaques
  |
  v
Leitura operacional para priorizacao
```

### Fluxo Perfil

```text
Usuario autenticado
  |
  v
/perfil/
  |
  v
Documentos SEI vinculados
  |
  v
Filtros por texto, participacao e periodo
  |
  v
Visualizacao e exportacao CSV
```
