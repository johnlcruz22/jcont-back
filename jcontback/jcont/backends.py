from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.utils import timezone

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

def check_cnpj(request):
    cnpj = request.GET.get('cnpj')
    exists = Loja.objects.filter(cnpj=cnpj).exists()
    return JsonResponse({'exists': exists})
