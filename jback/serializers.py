from rest_framework import serializers
from .models import CustomUser, Loja, Tecnico
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model        = CustomUser
        fields       = ('id', 'username', 'email', 'password', 'tipo')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": "Este e-mail já está cadastrado."})
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email   =validated_data['email'],
            password=validated_data['password'],
            tipo    =validated_data['tipo']
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
    

class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loja
        fields = '__all__'

    def validate_cpf(self, value):
        tecnico = self.instance
        if tecnico and Loja.objects.filter(cpf=value).exclude(id=tecnico.id).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        return value
    
class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnico
        fields = '__all__'