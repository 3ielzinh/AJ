# Changelog

Todas as mudancas relevantes deste projeto devem ser documentadas aqui.

O formato segue uma adaptacao simples de Keep a Changelog, com secoes por versao.

## 0.8.1 - Em andamento

- Criacao da base de governanca para agentes com `AGENTS.md`.
- Criacao do registro de decisoes arquiteturais em `docs/adr/`.
- Criacao de `ROADMAP.md` e `TODO.md`.
- Organizacao inicial do historico do projeto em changelog.
- Criacao de prompts reutilizaveis em `.ai/prompts/`.
- Criacao do `QA Agent` e da esteira automatizada de code review.
- Criacao da memoria do projeto em `.ai/context/`.
- Novo comando `importar_gestao_objetos` para importar planilhas de Gestao de Objetos em `Demanda` com `tipo=gestao_objetos`.
- Dry-run analitico para preflight de abas, candidatos, grupos, duplicidades, datas invalidas e valores inesperados sem gravacao.
- Importacao idempotente com `update_or_create`, resumo por aba e bloqueio de seguranca para nomes repetidos em grupos diferentes.
- Suporte a chave de idempotencia configuravel (`nome-tipo` ou `nome-grupo-tipo`) para evitar colisao de homonimos entre grupos.
- Nova visualizacao especifica para `/monitoramento/gestao-objetos/`, com UX de catalogo pesquisavel, KPIs proprios e filtros por metadados do objeto.
- Extracao segura de campos estruturados da importacao em `observacoes` para exibicao detalhada sem alterar o model `Demanda`.
- Ajuste da visualizacao de Gestao de Objetos para tabela mais limpa, com detalhes no colapso e correcao dos KPIs de fluxo.
- Criacao do model `ObjetoGestao`, com cadastro/edicao/exclusao proprios para o catalogo de Gestao de Objetos.
- Migracao dos registros legados de `Demanda(tipo=gestao_objetos)` para `ObjetoGestao`, preservando referencia da demanda de origem.
- Atualizacao do comando `importar_gestao_objetos` para gravar diretamente no catalogo `ObjetoGestao`.
- Remocao do acesso ao Design System da navegacao e da home, mantendo a referencia como rota interna.
- Reposicionamento do acesso ao Django Admin para dentro do Perfil, restrito a superusuarios.

## 0.8.0

- Dashboard de monitoramento com KPIs, graficos e destaque para demandas antigas ou em atraso.
- Perfil de usuario com consolidacao documental do SEI.
- Hub de monitoramento com entrada para monitoramento sistemico, SEI e area AJ.
- Reordenacao de prioridades por categoria.
- Melhorias no design system proprio.
- Fluxo de criacao, edicao e exclusao de demandas.

## 0.7.0

- Monitoramento sistemico de demandas com filtros e tabs por categoria.
- Consulta de processos e documentos SEI.
- Estrutura inicial de templates, componentes e CSS modular.
- Setup de desenvolvimento com Django, Docker e fixtures.
