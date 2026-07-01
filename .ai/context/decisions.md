# Decisions

Memoria curta de decisoes do projeto. Decisoes duradouras devem ter ADR em `docs/adr/`.

## Decisoes atuais

### Design system proprio

- Decisao: manter CSS modular proprio e nao usar Bootstrap.
- Motivo: consistencia visual e menor custo de manutencao.
- ADR: `docs/adr/001-design-system.md` e `docs/adr/005-css.md`.

### Monitoramento no app `monitoramento`

- Decisao: concentrar demandas, dashboard, SEI e prioridades no app `monitoramento`.
- Motivo: esses fluxos compoem o mesmo dominio operacional.
- ADR: `docs/adr/002-monitoramento.md` e `docs/adr/003-sei.md`.

### Prioridade manual por categoria

- Decisao: permitir reordenacao manual de prioridades.
- Motivo: a prioridade real depende de leitura operacional da equipe.
- ADR: `docs/adr/004-prioridades.md`.

### Memoria de agentes em `.ai/context/`

- Decisao: registrar regras de negocio, arquitetura, estilo, problemas conhecidos e FAQ em arquivos estaveis.
- Motivo: reduzir repeticao de contexto e evitar que agentes resolvam novamente problemas ja tratados.
- Status: aceita.
