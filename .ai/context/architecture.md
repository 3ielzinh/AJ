# Architecture

Memoria arquitetural do AJ.

## Stack

- Django
- PostgreSQL em Docker
- SQLite em desenvolvimento local quando necessario
- Docker e Docker Compose
- Templates Django
- CSS modular proprio

## Apps

### `core`

Responsavel por:

- home
- perfil do usuario
- pagina de referencia do design system
- fluxos transversais

### `monitoramento`

Responsavel por:

- demandas
- lista sistemica
- dashboard
- reordenacao de prioridade
- consulta SEI
- comandos de importacao

## Fluxo de requisicao

```text
Usuario -> URL -> View -> Form/Service/Query -> Model -> Banco -> Template -> HTML/CSS
```

## Dados

- Banco principal previsto: PostgreSQL.
- Banco local pode usar SQLite para desenvolvimento.
- Fixtures em `fixtures/` apoiam sincronizacao e carga inicial.

## Pontos de evolucao

- Criar camada de services quando dashboards, importacoes ou consolidacoes ficarem grandes demais para views.
- Registrar novas decisoes arquiteturais em `docs/adr/`.
- Separar integracoes externas se o fluxo SEI crescer alem de importacao e consulta.
