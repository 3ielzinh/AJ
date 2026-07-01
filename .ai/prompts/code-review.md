# Prompt: Code Review Automatizado

Use este prompt depois de toda implementacao relevante.

## Esteira obrigatoria

1. Implementador: entrega a mudanca e descreve objetivo.
2. Backend Agent: revisa models, views, forms, services, ORM, permissoes e URLs.
3. Reviewer Agent: procura regressao, seguranca, legibilidade, manutencao e lacunas de teste.
4. QA Agent: define e executa validacoes possiveis; lista testes manuais restantes.
5. Documentation Agent: atualiza documentos afetados.

## Entrada

- objetivo da mudanca:
- arquivos alterados:
- fluxos afetados:
- comandos ja executados:
- duvidas ou riscos conhecidos:

## Checklist do Backend Agent

- Consultas ORM estao corretas e eficientes?
- Validacoes estao no lugar certo?
- Permissoes e autenticacao foram consideradas?
- Models, forms e views respeitam os padroes locais?
- Ha impacto em migrations ou fixtures?

## Checklist do Reviewer Agent

- Existe regressao funcional provavel?
- Ha risco de seguranca ou exposicao de dado?
- Ha duplicacao desnecessaria?
- A mudanca respeita `AGENTS.md`, `.ai/context/` e `.ai/rules/`?
- Ha lacunas de teste relevantes?

## Checklist do QA Agent

- `manage.py check` foi executado quando aplicavel?
- Fluxos felizes e vazios foram considerados?
- Erros de validacao foram considerados?
- Exportacoes, filtros e ordenacoes foram conferidos quando afetados?

## Checklist do Documentation Agent

- `README.md` precisa mudar?
- `CHANGELOG.md` precisa receber item?
- `ROADMAP.md` ou `TODO.md` mudaram?
- Alguma ADR deve ser criada ou atualizada?
- `.ai/context/known-problems.md` ou `.ai/context/decisions.md` deve ser atualizado?

## Saida esperada

- Achados por severidade.
- Correcoes aplicadas.
- Validacoes executadas.
- Documentacao atualizada.
- Riscos residuais.
