Sempre reutilizar `tokens.css`, `base.css` e `components.css`.

Evitar CSS isolado por página quando um padrão compartilhado puder ser extraído ou reaproveitado.

Preservar o padrão visual aplicado em Home, Perfil, Monitoramento e Dashboard.

Usar as variantes de botão já existentes, como `btn--primary`, `btn--secondary`, `btn--ghost` e `btn--danger`.

Manter page headers, filtros, cards e tabelas coerentes com os componentes compartilhados do projeto.

Quando uma nova tela exigir refinamento visual, começar pela linguagem já consolidada no design system antes de experimentar novas soluções.

A rota `core:design_system` deve continuar sendo referência visual para manutenção da interface.

Após alterações em templates, rodar `manage.py check`.
