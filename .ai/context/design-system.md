# Design System

Memoria do design system do AJ.

## Objetivo

Manter interface institucional, consistente e operacional para home, perfil, monitoramento, dashboard, formularios e reordenacao.

## Arquivos principais

- `static/css/tokens.css`: variaveis de cor, espacamento, raio, sombra e tipografia.
- `static/css/base.css`: base visual global.
- `static/css/components.css`: componentes reutilizaveis.
- `templates/components/`: componentes Django compartilhados.
- `core/templates/core/design_system.html`: referencia visual restrita a usuarios staff.

## Regras

- Nao usar Bootstrap.
- Nao criar CSS inline.
- Reutilizar componentes existentes antes de criar novos.
- Manter telas operacionais densas, legiveis e sem aspecto de landing page.
- Evitar duplicacao de padroes entre paginas.

## Quando criar componente novo

Crie componente novo quando:

- aparecer em mais de uma tela;
- representar uma acao, card, badge, campo ou empty state recorrente;
- reduzir duplicacao real de HTML ou CSS.

## Validacao visual

- Conferir estados vazios.
- Conferir responsividade basica.
- Conferir contraste e hierarquia.
- Conferir se textos cabem nos controles.
