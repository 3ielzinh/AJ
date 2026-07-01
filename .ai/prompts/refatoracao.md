# Prompt: Refatoracao

Use este prompt para melhorar estrutura sem mudar comportamento esperado.

## Contexto obrigatorio

1. Leia `AGENTS.md`.
2. Leia `.ai/context/coding-style.md`.
3. Leia `.ai/context/architecture.md`.
4. Leia `.ai/rules/django.md`.

## Pedido

Quero refatorar:

- arquivo ou fluxo:
- motivo:
- comportamento que deve permanecer igual:
- limites da refatoracao:

## Regras

- Nao misturar refatoracao com nova funcionalidade.
- Manter mudancas pequenas e revisaveis.
- Preservar nomes de dominio quando eles forem claros para o negocio.
- Extrair services ou helpers apenas quando reduzir complexidade real.
- Atualizar ADR se a refatoracao estabelecer um novo padrao duradouro.

## Validacao

- Comparar comportamento antes/depois.
- Rodar `manage.py check`.
- Informar risco funcional e pontos que merecem QA manual.
