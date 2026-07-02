from django.urls import path
from . import views

app_name = "monitoramento"

urlpatterns = [
    # Hub de monitoramentos
    path("", views.MonitoramentoHubView.as_view(), name="hub"),
    path("sei/", views.MonitoramentoSEIView.as_view(), name="sei"),
    path("aj/", views.MonitoramentoAJView.as_view(), name="aj"),

    # Monitoramento Sistemico (visão atual)
    path("sistemico/", views.DemandaListView.as_view(), name="lista"),

    # Visões por categoria
    path("evolutivas/",         views.EvolutivaListView.as_view(),        name="evolutivas"),
    path("corretivas/",         views.CorretivaListView.as_view(),        name="corretivas"),
    path("gestao-objetos/",     views.GestaoObjetosListView.as_view(),    name="gestao_objetos"),
    path("gestao-objetos/novo/", views.ObjetoGestaoCreateView.as_view(),  name="gestao_objeto_criar"),
    path("gestao-objetos/<int:pk>/editar/", views.ObjetoGestaoUpdateView.as_view(), name="gestao_objeto_editar"),
    path("gestao-objetos/<int:pk>/excluir/", views.ObjetoGestaoDeleteView.as_view(), name="gestao_objeto_excluir"),
    # Rotas legadas (mantidas por compatibilidade)
    path("indicacao-rubrica/",  views.IndicacaoRubricaListView.as_view(), name="indicacao_rubrica"),
    path("criacao-objeto/",     views.CriacaoObjetoListView.as_view(),    name="criacao_objeto"),
    path("concluidas/",         views.ConcluídasListView.as_view(),       name="concluidas"),
    path("dashboard/",          views.DashboardView.as_view(),            name="dashboard"),

    # CRUD
    path("nova/",                  views.DemandaCreateView.as_view(),      name="criar"),
    path("<int:pk>/editar/",       views.DemandaUpdateView.as_view(),      name="editar"),
    path("<int:pk>/excluir/",      views.DemandaDeleteView.as_view(),      name="excluir"),
    path("reordenar/",             views.ReordenarPrioridadeView.as_view(), name="reordenar"),
]
