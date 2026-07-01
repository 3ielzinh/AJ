# Known Problems

Memoria de problemas conhecidos, investigados ou resolvidos. Use este formato para evitar que agentes repitam diagnosticos antigos.

## Template

### Problema

Descreva o comportamento observado.

### Causa

Explique a causa identificada, se houver.

### Solucao

Explique a solucao adotada ou recomendada.

### Status

Aberto, em investigacao, resolvido ou monitorado.

### Referencias

Arquivos, PRs, commits, ADRs ou versoes relacionadas.

---

## Consultas lentas em dashboards

### Problema

Dashboards e filtros podem ficar lentos se acessarem relacoes em loop ou fizerem varias consultas por indicador.

### Causa

Risco tipico de N+1 queries e agregacoes repetidas em views ou templates.

### Solucao

Usar agregacoes do ORM, `select_related` e `prefetch_related` quando houver relacoes acessadas em lote.

### Status

Monitorado.

### Referencias

- `.ai/context/coding-style.md`
- `.ai/prompts/novo-dashboard.md`
