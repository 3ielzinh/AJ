# AJ Development Guide

## Projeto

Sistema interno da CGPJU desenvolvido em Django para monitoramento de demandas, consulta de informacoes do SEI, dashboard operacional, perfil de usuario e organizacao do fluxo de trabalho da Assessoria Juridica.

## Arquitetura

- Django
- PostgreSQL em Docker e SQLite para desenvolvimento local quando necessario
- Docker e Docker Compose
- Design System proprio
- CSS modular em `static/css/`
- Templates Django com componentes reutilizaveis
- Apps principais: `core` e `monitoramento`

## Estrutura principal

- `config/`: settings, urls, ASGI e WSGI.
- `core/`: home, perfil e pagina de referencia do design system.
- `monitoramento/`: demandas, dashboard, reordenacao, monitoramento SEI e comandos de importacao.
- `templates/`: layouts e componentes globais.
- `static/css/`: tokens, base e componentes visuais compartilhados.
- `.ai/context/`: contexto funcional do produto.
- `.ai/rules/`: regras de desenvolvimento para agentes.
- `.ai/prompts/`: prompts reutilizaveis para tarefas recorrentes.
- `.ai/agents/`: papeis especializados para backend, frontend, review, QA, docs, DBA e DevOps.
- `docs/adr/`: decisoes arquiteturais registradas.

## Nunca faca

- Nao criar CSS inline em templates.
- Nao duplicar componentes ja existentes em `templates/components/` ou `static/css/components.css`.
- Nao usar Bootstrap ou bibliotecas visuais novas sem decisao registrada.
- Nao alterar `static/css/tokens.css` sem necessidade clara.
- Nao misturar regra de negocio complexa diretamente em templates.
- Nao versionar segredos, credenciais, bancos locais ou arquivos gerados.
- Nao reverter alteracoes existentes sem entender se foram feitas por outra pessoa ou agente.

## Sempre faca

- Reutilizar `components.css`, `base.css` e os componentes de template antes de criar estilos novos.
- Manter consistencia visual com home, perfil, monitoramento, dashboard e formularios.
- Utilizar CBV quando possivel e quando encaixar no padrao local.
- Manter views enxutas; mover consultas ou consolidacoes complexas para funcoes auxiliares ou services quando o fluxo crescer.
- Rodar `manage.py check` apos alteracoes em models, views, urls, settings ou templates relevantes.
- Manter nomes claros em portugues quando o dominio for institucional.
- Atualizar documentacao quando a mudanca alterar fluxo, arquitetura, operacao ou decisao de produto.

## Antes de alterar

Leia, nesta ordem, quando existirem:

1. `AGENTS.md`
2. `.ai/context/`
3. `.ai/rules/`
4. `.ai/prompts/`, quando existir prompt para a tarefa
5. `README.md`
6. `docs/adr/`

Para mudancas de interface, consulte tambem:

- `static/css/tokens.css`
- `static/css/base.css`
- `static/css/components.css`
- `core/templates/core/design_system.html`

## Apos alterar

Explique:

- arquivos alterados
- impacto funcional
- impacto visual, se houver
- comandos de validacao executados
- possiveis riscos ou pontos que merecem revisao humana

## Esteira apos implementacao

Para toda implementacao relevante, use o fluxo descrito em `.ai/prompts/code-review.md`:

1. Implementador entrega a mudanca.
2. Backend Agent revisa impacto em Django, ORM, forms, views, permissoes e URLs.
3. Reviewer Agent procura bugs, regressao, seguranca, manutencao e lacunas de teste.
4. QA Agent valida comandos, fluxos felizes, estados vazios, filtros, ordenacao e erros.
5. Documentation Agent atualiza README, changelog, roadmap, TODO, ADRs ou memoria em `.ai/context/`.

## Validacao rapida

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py check
```

## Convencoes de agentes

- Prefira mudancas pequenas, coesas e documentadas.
- Ao criar uma decisao duradoura, registre uma ADR em `docs/adr/`.
- Ao concluir uma entrega relevante, atualize `CHANGELOG.md`.
- Ao planejar evolucoes futuras, atualize `ROADMAP.md`.
- Ao identificar pendencias, atualize `TODO.md`.
- Ao aprender regra, problema ou decisao do produto, atualize `.ai/context/`.
