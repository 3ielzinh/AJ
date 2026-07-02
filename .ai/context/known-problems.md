# Known Problems

Memoria de problemas conhecidos, investigados ou resolvidos. Use este formato para evitar que agentes repitam diagnosticos antigos.

## Template

### Problema (modelo)

Descreva o comportamento observado.

### Causa (modelo)

Explique a causa identificada, se houver.

### Solucao (modelo)

Explique a solucao adotada ou recomendada.

### Status (modelo)

Aberto, em investigacao, resolvido ou monitorado.

### Referencias (modelo)

Arquivos, PRs, commits, ADRs ou versoes relacionadas.

---

## Consultas lentas em dashboards

### Problema (dashboard)

Dashboards e filtros podem ficar lentos se acessarem relacoes em loop ou fizerem varias consultas por indicador.

### Causa (dashboard)

Risco tipico de N+1 queries e agregacoes repetidas em views ou templates.

### Solucao (dashboard)

Usar agregacoes do ORM, `select_related` e `prefetch_related` quando houver relacoes acessadas em lote.

### Status (dashboard)

Monitorado.

### Referencias (dashboard)

- `.ai/context/coding-style.md`
- `.ai/prompts/novo-dashboard.md`

---

## Importacao de Gestao de Objetos com nome duplicado

### Problema (gestao de objetos)

No arquivo `Higienizacao_AJ_grupos.xlsx`, pode haver `NOME DO OBJETO` repetido em grupos diferentes.

### Causa (gestao de objetos)

A chave de idempotencia sugerida (`nome + tipo`) nao diferencia objetos homonimos em grupos distintos.

### Solucao (gestao de objetos)

Rodar dry-run do comando `importar_gestao_objetos`, detectar duplicidade entre grupos e bloquear a importacao real ate definir chave mais segura (por exemplo `nome + classificacao + tipo` ou outra regra validada com o negocio).

### Status (gestao de objetos)

Aberto.

### Referencias (gestao de objetos)

- `monitoramento/management/commands/importar_gestao_objetos.py`
