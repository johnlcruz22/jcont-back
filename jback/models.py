from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

#MODELS STATIC
class Nivel(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao

class TipoAcesso(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao


#MODELS CUSTOM
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, tipo=None, **extra_fields):
        
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user  = self.model(username=username, email=email, tipo=tipo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    username    = models.CharField(max_length=150, unique=True)
    email       = models.EmailField(unique=True)
    last_login  = models.DateTimeField(null=True, blank=True)
    tipo        = models.ForeignKey(TipoAcesso, on_delete=models.SET_NULL, null=True)  # 1 para master, 2 para comum, 3 para técnico
        
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Loja(models.Model):
    nome        = models.CharField(max_length=255)
    cnpj        = models.CharField(max_length=18, unique=True)
    endereco    = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cidade      = models.CharField(max_length=255)
    email       = models.EmailField()
    telefone    = models.CharField(max_length=15)
    estado      = models.CharField(max_length=2)
    cep         = models.CharField(max_length=9)

    def __str__(self):
        return self.nome
    
class Tecnico(AbstractBaseUser):
    nome        = models.CharField(max_length=30)
    email       = models.EmailField(unique=True)
    telefone    = models.CharField(max_length=15)
    cpf         = models.CharField(max_length=14, unique=True)
    endereco    = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cidade      = models.CharField(max_length=255)
    estado      = models.CharField(max_length=2)
    cep         = models.CharField(max_length=9)
    nivel       = models.ForeignKey(Nivel, on_delete=models.SET_NULL, null=True)
    habilitado  = models.BooleanField(default=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Criação de um login na tabela CustomUser ao salvar o Técnico
        if not CustomUser.objects.filter(email=self.email).exists():
            CustomUser.objects.create_user(
                username=self.nome,
                email=self.email,
                password='mudar123',  # Você pode definir uma senha padrão ou gerar uma aleatória
                tipo=TipoAcesso.objects.get(descricao='técnico'),
                nivel=self.nivel,
                habilitado=self.habilitado
            )
        super().save(*args, **kwargs)    

