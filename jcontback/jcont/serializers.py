from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import (
    CustomUser, 
    Loja, 
    TipoServico, 
    CNAE, 
    TipoRegime, 
    RamoAtividade, 
    Cliente, 
    ClienteExcel,
    DadosReferencia
)



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'tipo')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": "Este e-mail já está cadastrado."})
        return value

    def create(self, validated_data):
        tipo = validated_data.get('tipo', 1)  # Default tipo to 1 if not provided
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            tipo=tipo
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        UserModel = get_user_model()
        user = UserModel.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        return attrs
    
class LojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loja
        fields = '__all__'

    def validate_cnpj(self, value):
        loja = self.instance
        if loja and Loja.objects.filter(cnpj=value).exclude(id=loja.id).exists():
            raise serializers.ValidationError("Este CNPJ já está cadastrado.")
        return value
  
class LojaListViewSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loja
        fields = ['id', 'nome'] 
         
class TipoServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServico
        fields = ['id', 'descricao']

class TipoRegimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRegime
        fields = ['id', 'descricao']
        
class RamoAtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RamoAtividade
        fields = ['id', 'descricao']
              
class CNAESelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CNAE
        fields = ['id', 'codigo']  # Apenas os campos necessários
        
class ClienteSerializer(serializers.ModelSerializer):
    regime_tributario_descricao = serializers.CharField(source='regime_tributario.descricao', read_only=True)
    cnae_principal_descricao    = serializers.CharField(source='cnae_principal.descricao', read_only=True)
    ramo_atividade_descricao    = serializers.CharField(source='ramo_atividade.descricao', read_only=True)
    cnae_principal_codigo       = serializers.CharField(source='cnae_principal.codigo', read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id',
            'razao_social',
            'cnpj',
            'apelido_cliente',
            'estado',
            'ramo_atividade',
            'ramo_atividade_descricao',
            'regime_tributario',  # Este é usado para gravação (FK)
            'regime_tributario_descricao',  # Somente leitura
            'cnae_principal',  # Este é usado para gravação (FK)
            'cnae_principal_descricao',
            'cnae_principal_codigo'  # Somente leitura
        ]
        
class ClienteExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteExcel
        fields = '__all__'

class DadosReferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadosReferencia
        fields = '__all__'