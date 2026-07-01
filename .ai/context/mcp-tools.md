# MCP Tools

Memoria da configuracao MCP usada no ambiente Codex deste projeto.

## Configuracao aplicada

Arquivo global:

- `C:\Users\gabriel.jorge\.codex\config.toml`

Backup criado antes da alteracao:

- `C:\Users\gabriel.jorge\.codex\config.toml.bak-20260701-121758`

Junction ASCII para evitar problemas com caminhos acentuados:

- `C:\Users\gabriel.jorge\.codex\workspaces\AJ`
- aponta para a raiz real do projeto Django `AJ`

## Servidores configurados

- Serena: analise semantica, simbolos, referencias e memoria de codigo.
- Context7: documentacao atualizada de bibliotecas.
- Filesystem: acesso controlado ao projeto pelo caminho junction.
- Postgres: leitura do banco `aj_dev` em `localhost:5432`.
- Playwright: automacao de navegador via MCP.
- Memory: memoria persistente em grafo.
- Sequential Thinking: raciocinio estruturado por etapas.
- Fetch: busca e leitura de URLs.
- SQLite: acesso ao `db.sqlite3` local.

## Ja existente no Codex

- Browser plugin estava habilitado.
- GitHub connector/plugin ja estava disponivel no ambiente Codex.
- Node REPL ja estava configurado.

## Pendencias

- Docker CLI nao esta disponivel no PATH. Para habilitar Docker MCP ou uso direto de containers, instalar Docker Desktop ou expor `docker.exe` no PATH.
- Postgres MCP depende do banco estar rodando em `localhost:5432` com `postgres:postgres` e banco `aj_dev`.
- A configuracao MCP nova pode exigir reinicio da janela/sessao Codex para carregar todos os servidores.

## Validacoes executadas

- `uv` instalado via `python -m pip install --user uv`.
- Serena instalado via `uv tool install -p 3.13 serena-agent`.
- `serena init` executado.
- `serena project health-check` passou com PATH ajustado.
- `config.toml` validado com `tomllib`.
- `hooks.json` validado com `json`.
