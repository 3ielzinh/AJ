# ADR 002: Monitoramento Como App Dedicado

## Status

Aceita

## Contexto

O monitoramento de demandas e o principal fluxo operacional do sistema. Ele inclui lista sistemica, filtros, tabs, dashboard, CRUD, categorias, status e reordenacao de prioridades.

## Decisao

Concentrar esse dominio no app `monitoramento`, mantendo models, forms, views, urls, templates e comandos relacionados no mesmo limite funcional.

## Consequencias

- O dominio de demandas fica mais facil de localizar e evoluir.
- O app `core` permanece focado em paginas institucionais, perfil e suporte geral.
- Consultas muito complexas podem exigir camada de services no futuro para evitar views grandes demais.
