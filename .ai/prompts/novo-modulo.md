# Prompt: Novo Modulo

Use este prompt quando precisar criar um novo modulo, app Django ou area funcional no AJ.

## Contexto obrigatorio

Antes de propor ou implementar:

1. Leia `AGENTS.md`.
2. Leia `.ai/context/architecture.md`.
3. Leia `.ai/context/business-rules.md`.
4. Leia `.ai/rules/django.md`.
5. Consulte ADRs em `docs/adr/` se a decisao tiver impacto duradouro.

## Pedido

Quero criar um novo modulo para:

- objetivo:
- usuarios envolvidos:
- dados manipulados:
- rotas esperadas:
- telas esperadas:
- permissoes:
- integracoes:

## Entrega esperada

- Desenhar a arquitetura minima.
- Criar ou alterar models, forms, views, urls e templates conforme necessario.
- Reutilizar o design system existente.
- Evitar duplicacao com apps existentes.
- Atualizar `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `TODO.md` ou ADRs quando aplicavel.

## Validacao

- Rodar `manage.py check`.
- Indicar testes manuais recomendados.
- Explicar arquivos alterados, impactos e riscos.
