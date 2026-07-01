# Prompt: Novo Dashboard

Use este prompt para criar ou evoluir dashboards, indicadores e visualizacoes agregadas.

## Contexto obrigatorio

1. Leia `AGENTS.md`.
2. Leia `.ai/context/architecture.md`.
3. Leia `.ai/context/design-system.md`.
4. Leia `.ai/context/known-problems.md`.
5. Consulte `monitoramento/views.py` e templates de dashboard existentes.

## Pedido

Quero criar ou alterar um dashboard com:

- objetivo operacional:
- indicadores:
- filtros:
- periodo de analise:
- publico-alvo:
- origem dos dados:
- exportacoes necessarias:

## Regras

- Priorizar indicadores acionaveis, nao apenas numeros decorativos.
- Evitar consultas repetidas ou N+1.
- Reutilizar tokens e componentes do design system.
- Manter hierarquia visual densa, clara e institucional.
- Documentar regra de negocio dos KPIs em `.ai/context/business-rules.md` quando necessario.

## Validacao

- Rodar `manage.py check`.
- Conferir dashboard com base vazia, base pequena e base com muitos registros.
- Registrar riscos de performance.
