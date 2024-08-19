from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer, LojaSerializer, TecnicoSerializer
from .models import CustomUser, Loja, Tecnico, TipoAcesso
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from django.views import View
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


#LOGIN
class RegisterView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            print(e)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []  # Permitir acesso público

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


#LOJA
class LojaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LojaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LojaListView(generics.ListAPIView):
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer
    permission_classes = [IsAuthenticated]
    
class LojaDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

class LojaDetailAPIView(generics.RetrieveAPIView):
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
  
class LojaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        loja = get_object_or_404(Loja, id=id)
        loja.delete()
        return JsonResponse({'message': 'Loja excluída com sucesso!'}, status=200)


#GENERICOS
class CheckCNPJView(View):
    def get(self, request, *args, **kwargs):
        cnpj = request.GET.get('cnpj')
        exists = Loja.objects.filter(cnpj=cnpj).exists()
        return JsonResponse({'exists': exists})
      
#TECNICO
class TecnicoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tecnico_data = request.data
        tecnico_serializer = TecnicoSerializer(data=tecnico_data)
        
        if tecnico_serializer.is_valid():
            tecnico = tecnico_serializer.save()
            
            # Criação de usuário correspondente ao Técnico
            CustomUser.objects.create_user(
                username=tecnico.nome,
                email=tecnico.email,
                password=tecnico_data.get('password'),  # Certifique-se de que a senha esteja no request
                tipo=TipoAcesso.objects.get(descricao='técnico')
            )
            
            return Response(tecnico_serializer.data, status=status.HTTP_201_CREATED)
        return Response(tecnico_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TecnicoListView(generics.ListAPIView):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer
    permission_classes = [IsAuthenticated]
    
class TecnicoDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

class TecnicoDetailAPIView(generics.RetrieveAPIView):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
  
class TecnicoDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        loja = get_object_or_404(Tecnico, id=id)
        loja.delete()
        return JsonResponse({'message': 'Tecnico excluída com sucesso!'}, status=200)

