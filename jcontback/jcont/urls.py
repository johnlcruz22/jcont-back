from django.urls import path
from .views import (
    RegisterView,
    CheckCNPJView,
    LoginView,
    CustomUserDeleteView,
    TipoServicoListView,
    CNAESelectListView,
    TipoRegimeListView,
    RamoAtividadeListView,
    ClienteCreateView,
    ClienteListView,
    UploadExcelView,
    CompareDadosView,
    CorrigirDadosView,
    UploadBaseExcelView,
    ClienteExcelDetailView,
    AtualizarClienteView,
    DownloadExcelView
)

urlpatterns = [
    #ROTAS LOGIN
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    #ROTA CUSTOMUSER
    path('user/delete/<str:email>/', CustomUserDeleteView.as_view(), name='delete_user'),
    
    #ROTAS GENERICAS
    path('tipos-servico/',  TipoServicoListView.as_view(), name='tipos-servico-list'),
    path('tipos-regime/',   TipoRegimeListView.as_view(), name='tipos-regime-list'),
    path('ramoatividade/',  RamoAtividadeListView.as_view(), name='ramo-atividade-list'),
    path('cnaes/select/',   CNAESelectListView.as_view(), name='cnae-select-list'),


    #ROTAS CLIENTE
    path('cliente/create/', ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/',       ClienteListView.as_view(), name='clientes-list'), 
    
    #ROTAS ARQUIVO
    path('upload/<int:id>/',    UploadExcelView.as_view(), name='upload-excel'),
    path('upload-base/',        UploadBaseExcelView.as_view(), name='upload-base-excel'),
    path('comparar/<int:id>/',  CompareDadosView.as_view(), name='compare-dados'),
    path('getdados/<int:id>/',  ClienteExcelDetailView.as_view(), name='get-dados'),
    
    path('corrigir/<int:id>/',  CorrigirDadosView.as_view(), name='corrigir-dados'),
    path('salvar/',             AtualizarClienteView.as_view(), name='salvar-dados'),
    path('download/<int:id>/',  DownloadExcelView.as_view(), name='download-excel'),

    
]
