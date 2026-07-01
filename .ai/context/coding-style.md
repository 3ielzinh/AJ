# Coding Style

Padroes de codigo para manter o AJ consistente.

## Django

- Prefira nomes claros em portugues para conceitos de dominio.
- Use CBV quando ela simplificar CRUD, listagem ou formularios.
- Use FBV quando o fluxo for simples ou quando o padrao existente do arquivo for FBV.
- Mantenha views legiveis; extraia consultas ou consolidacoes complexas quando crescerem demais.
- Forms devem concentrar validacoes de entrada do usuario.
- Models devem manter regras estruturais e representacoes claras.

## ORM

- Use `select_related` e `prefetch_related` quando houver relacoes acessadas em loop.
- Evite consultas repetidas dentro de templates.
- Para dashboards, prefira agregacoes explicitas e nomes de variaveis descritivos.

## Templates

- Nao usar CSS inline.
- Reutilizar `templates/components/` quando possivel.
- Evitar regra de negocio complexa no template.
- Manter textos objetivos e alinhados ao glossario do projeto.

## CSS

- Reutilizar `static/css/tokens.css`, `base.css` e `components.css`.
- Criar classe nova apenas quando houver necessidade clara.
- Nao introduzir Bootstrap.
- Nao alterar tokens sem justificativa.

## Documentacao

- Atualizar `CHANGELOG.md` em entregas relevantes.
- Criar ADR para decisoes duradouras.
- Atualizar memoria em `.ai/context/` quando uma regra nova for aprendida.
