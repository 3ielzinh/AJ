# ADR 001: Design System Proprio

## Status

Aceita

## Contexto

O AJ possui varias telas operacionais, como home, perfil, monitoramento, dashboard, formularios e reordenacao de prioridades. A experiencia precisa ser consistente, institucional e facil de manter sem depender de bibliotecas visuais externas.

## Decisao

Manter um design system proprio baseado em:

- `static/css/tokens.css`
- `static/css/base.css`
- `static/css/components.css`
- componentes em `templates/components/`
- pagina de referencia em `core/templates/core/design_system.html`

Novos estilos devem reaproveitar esses arquivos antes de criar CSS especifico por pagina.

## Consequencias

- A interface fica mais consistente entre fluxos.
- Mudancas visuais globais passam por poucos arquivos.
- E necessario cuidado para nao duplicar componentes nem criar CSS inline.
- Alteracoes em tokens devem ser raras e justificadas.
