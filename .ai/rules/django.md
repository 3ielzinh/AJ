Sempre validar alterações estruturais com `.\\venv\\Scripts\\python.exe manage.py check`.

Preferir correções na origem do problema, especialmente em templates, views e formulários.

Antes de editar templates Django, confirmar qual view alimenta o contexto da página.

Ao alterar filtros, listagens ou dashboards, preservar os nomes de parâmetros já usados nas rotas e templates.

Evitar duplicação de markup entre templates parecidos; preferir manter fluxos compartilhados no mesmo template quando já for assim no projeto.

Não introduzir dependências novas para resolver problemas que já podem ser resolvidos com Django, CSS e JavaScript nativo.

Preservar compatibilidade com as rotas existentes em `core/urls.py` e `monitoramento/urls.py`.

Em mudanças de CRUD, não quebrar os fluxos de criação, edição, exclusão, reordenação e dashboard do monitoramento.
