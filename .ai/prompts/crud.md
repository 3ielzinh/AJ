# Prompt: CRUD

Use este prompt para criar ou evoluir um CRUD no AJ.

## Contexto obrigatorio

1. Leia `AGENTS.md`.
2. Leia `.ai/context/architecture.md`.
3. Leia `.ai/context/coding-style.md`.
4. Leia `.ai/context/design-system.md`.
5. Leia `.ai/rules/django.md` e `.ai/rules/frontend.md`.

## Pedido

Quero um CRUD para:

- entidade:
- campos:
- regras de validacao:
- permissoes:
- filtros:
- ordenacao:
- exportacao:
- relacoes com outros modelos:

## Padrao esperado

- Model claro e migracao quando necessario.
- Form com validacoes de entrada.
- Views alinhadas aos padroes existentes, preferindo CBV quando fizer sentido.
- URLs nomeadas.
- Templates reutilizando layout e componentes globais.
- Mensagens de sucesso/erro consistentes.

## Validacao

- Criar, listar, editar e excluir.
- Testar formulario invalido.
- Testar usuario sem permissao quando aplicavel.
- Rodar `manage.py check`.
