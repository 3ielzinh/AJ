# Business Rules

Memoria das regras de negocio do AJ. Atualize quando uma regra funcional for criada, alterada ou esclarecida.

## Demandas

- Demandas representam itens de acompanhamento operacional da CGPJU.
- Status, tipo, categoria, datas, reiterações e observacoes impactam lista, dashboard e priorizacao.
- A prioridade manual deve ser respeitada na leitura operacional quando estiver configurada.

## Monitoramento

- A lista sistemica e a fonte principal para busca, filtro, criacao, edicao e exclusao de demandas.
- O dashboard deve consolidar indicadores acionaveis para apoiar gestao e priorizacao.
- Demandas antigas, urgentes ou sem movimentacao devem ser destacadas quando houver regra definida.
- Gestao de Objetos e tratada como catalogo operacional pesquisavel, nao como fila comum de demandas.
- Gestao de Objetos usa o model proprio `ObjetoGestao`; `Demanda(tipo=gestao_objetos)` deve ser tratado como legado/origem historica.
- Na importacao de Gestao de Objetos por planilha, a aba `Objeto` e apenas indice e nao deve gerar demanda.
- Na importacao de Gestao de Objetos, `ATIVO` deve alimentar o campo booleano `ativo` do catalogo quando o valor for seguro (`SIM`/`NAO`).
- Na importacao de Gestao de Objetos, `DATA ENCERRAMENTO` valida deve alimentar `ObjetoGestao.data_encerramento`.

## SEI

- Processos e documentos SEI servem como base documental para rastreabilidade.
- A participacao documental pode envolver criacao, edicao, analise ou assinatura.
- O perfil do usuario deve consolidar documentos vinculados ao usuario autenticado.

## Exportacoes

- Exportacoes devem refletir os filtros aplicados quando o fluxo assim indicar.
- CSV deve ter cabecalhos claros e dados suficientes para uso operacional.

## Pendencias de definicao

- Confirmar criterios oficiais de demanda atrasada.
- Confirmar regra final de urgencia por categoria.
- Confirmar campos obrigatorios definitivos para cada tipo de demanda.
