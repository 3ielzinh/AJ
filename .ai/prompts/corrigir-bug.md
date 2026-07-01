# Prompt: Corrigir Bug

Use este prompt quando houver erro funcional, visual, de dados ou de ambiente.

## Contexto obrigatorio

1. Leia `AGENTS.md`.
2. Leia `.ai/context/known-problems.md`.
3. Leia `.ai/context/faq.md`.
4. Consulte regras em `.ai/rules/`.

## Diagnostico

Bug observado:

- comportamento atual:
- comportamento esperado:
- rota/tela/comando afetado:
- dados de exemplo:
- mensagem de erro:
- quando comecou:

## Processo

1. Reproduzir ou explicar por que nao foi possivel reproduzir.
2. Identificar causa provavel.
3. Fazer a menor correcao segura.
4. Verificar impacto em fluxos relacionados.
5. Atualizar `.ai/context/known-problems.md` se o problema for recorrente ou importante.

## Validacao

- Rodar comando especifico do fluxo afetado.
- Rodar `manage.py check` se houver alteracao em Django.
- Explicar causa, solucao e risco residual.
