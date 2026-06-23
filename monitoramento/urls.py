from django.urls import path
from . import views

app_name = "monitoramento"

urlpatterns = [
    # Visão consolidada (todas as categorias)
    path("", views.DemandaListView.as_view(), name="lista"),

    # Visões por categoria
    path("evolutivas/",         views.EvolutivaListView.as_view(),        name="evolutivas"),
    path("corretivas/",         views.CorretivaListView.as_view(),        name="corretivas"),
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
