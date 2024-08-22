from django.urls import path
from .views import (
    RegisterView,
    CheckCNPJView,
    CheckCPFView,
    LoginView,
    LojaDeleteView,
    LojaCreateView,
    LojaListView,
    LojaDetailUpdateAPIView,
    LojaDetailAPIView,
    TecnicoDeleteView,
    TecnicoCreateView,
    TecnicoListView,
    TecnicoDetailUpdateAPIView,
    TecnicoDetailAPIView,
    CustomUserDeleteView,
)

urlpatterns = [
    #ROTAS LOGIN
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # ROTA CUSTOMUSER
    path('user/delete/<str:email>/', CustomUserDeleteView.as_view(), name='delete_user'),
    
    #ROTAS LOJAS
    path('lojas/create/',          LojaCreateView.as_view(), name='loja-create'),
    path('lojas/list/',            LojaListView.as_view(), name='lojas-list'),
    path('lojas/up/<int:id>/',     LojaDetailUpdateAPIView.as_view(), name='loja-detail-update'),
    path('lojas/<int:id>/',        LojaDetailAPIView.as_view(), name='loja-detail'),
    path('lojas/check-cnpj/',      CheckCNPJView.as_view(), name='check_cnpj'),
    path('lojas/delete/<int:id>/', LojaDeleteView.as_view(), name='delete_loja'),
    
    #ROTAS TECNICO
    path('tecnico/create/',          TecnicoCreateView.as_view(), name='tecnico-create'),
    path('tecnico/list/',            TecnicoListView.as_view(), name='tecnico-list'),
    path('tecnico/up/<int:id>/',     TecnicoDetailUpdateAPIView.as_view(), name='tecnico-detail-update'),
    path('tecnico/<int:id>/',        TecnicoDetailAPIView.as_view(), name='tecnico-detail'),
    path('tecnico/delete/<int:id>/', TecnicoDeleteView.as_view(), name='delete_tecnico'),
    path('tecnico/check-cpf/',       CheckCPFView.as_view(), name='check_cpf'),
]
