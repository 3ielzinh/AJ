# ADR 006: Gestao de Objetos como Catalogo Operacional

## Status

Aceita

## Contexto

A rota `/monitoramento/gestao-objetos/` herdava a mesma visualizacao da listagem comum de demandas (evolutivas/corretivas). A importacao da planilha de higienizacao trouxe registros com metadados tipicos de catalogo (ativo, carater, fluxo, tema, limite maximo, tipo de objeto e outros), muitos inicialmente preservados em `observacoes` com padrao estruturado.

Esse formato nao representa apenas uma fila de trabalho, e sim um catalogo operacional consultavel.

## Decisao

Criar o model dedicado `ObjetoGestao` para representar o catalogo operacional, mantendo `Demanda(tipo=gestao_objetos)` apenas como legado/origem historica quando existir.

Criar visualizacao especifica para `/monitoramento/gestao-objetos/` com:

- template proprio de catalogo;
- KPIs especificos de objetos;
- filtros por metadados do objeto (grupo, ativo, carater, fluxo, tema);
- tabela com poucas colunas orientadas a leitura rapida;
- detalhe expansivel por linha;
- formulario proprio para cadastro, edicao e exclusao de objetos;
- migracao de dados legados a partir de `Demanda(tipo=gestao_objetos)`.

## Consequencias

- Evolutivas, Corretivas e Concluidas permanecem na listagem comum sem regressao.
- Gestao de Objetos passa a ter experiencia operacional mais adequada ao dominio.
- Ha migracao de schema para `ObjetoGestao` e migracao de dados sem excluir as demandas legadas.
- Importacoes futuras devem gravar diretamente em `ObjetoGestao`.
- Regras finais de obrigatoriedade e validacao ainda podem evoluir.
