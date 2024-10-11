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

class TipoServico(models.Model):
    descricao = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descricao

class TipoRegime(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao    
    
class RamoAtividade(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao    
    
class CNAE(models.Model):
    codigo  = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    cod_setor = models.CharField(max_length=255, null=True, blank=True)
    nome_setor = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.codigo} - {self.descricao}'    
   
#MODELS CUSTOM
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, tipo=1, **extra_fields):
        
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

class Cliente(models.Model):
    razao_social        = models.CharField(max_length=255)
    cnpj                = models.CharField(max_length=20, unique=True)
    apelido_cliente     = models.CharField(max_length=255, blank=True, null=True)
    regime_tributario   = models.ForeignKey(TipoRegime, on_delete=models.SET_NULL, null=True)
    estado              = models.CharField(max_length=2)
    ramo_atividade      = models.ForeignKey(RamoAtividade, on_delete=models.SET_NULL, null=True)
    cnae_principal      = models.ForeignKey(CNAE, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.razao_social
    
class ClienteExcel(models.Model):
    cfop = models.CharField(max_length=10, default="0000")  # CFOP com valor default "0000"
    cod_prod = models.CharField(max_length=100)  # Cód Prod
    ncm = models.CharField(max_length=100)  # NCM
    descricao_banco = models.CharField(max_length=255)  # Descrição Prod
    cst_icms = models.CharField(max_length=10)  # CST ICMS
    cst_pis = models.CharField(max_length=10)  # CST PIS
    cst_cofins = models.CharField(max_length=10)  # CST COFINS
    id_cliente = models.CharField(max_length=100, null=False, blank=False)
    

    def __str__(self):
        return f'{self.cod_prod} - {self.ncm}'

class DadosReferencia(models.Model):

    tipo = models.CharField(max_length=20, default="NT")            
    codigo_original_tipi = models.CharField(max_length=10)
    codigo_sem_ponto = models.CharField(max_length=10)    
    descricao_tipi = models.CharField(max_length=255, default="NT")      
    ipi = models.CharField(max_length=9, default="NT")                 
    cst_pis = models.CharField(max_length=9, default="NT")             
    cst_cofins = models.CharField(max_length=9, default="NT")          
    cst_icms_sp = models.CharField(max_length=9, default="NT")         
    cst_icms_rj = models.CharField(max_length=9, default="NT")         
    cst_icms_es = models.CharField(max_length=9, default="NT")         
    cst_icms_mg = models.CharField(max_length=9, default="NT")    
    etc = models.CharField(max_length=9, default="NT")
    reducao = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return self.codigo_sem_ponto