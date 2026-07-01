# FAQ

Perguntas frequentes para agentes e mantenedores.

## Onde comecar antes de mudar codigo?

Leia `AGENTS.md`, depois `.ai/context/`, `.ai/rules/` e `README.md`.

## Quando atualizar `CHANGELOG.md`?

Quando a mudanca for relevante para usuario, manutencao, arquitetura, deploy, dados ou fluxo operacional.

## Quando criar uma ADR?

Quando a decisao tiver efeito duradouro, mudar padrao arquitetural, introduzir dependencia, alterar design system ou definir regra estrutural.

## Posso alterar `tokens.css`?

Sim, mas apenas com justificativa clara. Primeiro tente resolver com classes e componentes existentes.

## Posso usar Bootstrap?

Nao. O projeto usa design system proprio.

## Qual comando minimo de validacao Django?

```powershell
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
.\venv\Scripts\python.exe manage.py check
```

## Onde registrar bugs recorrentes?

Em `.ai/context/known-problems.md`, incluindo problema, solucao, status e versao quando possivel.
