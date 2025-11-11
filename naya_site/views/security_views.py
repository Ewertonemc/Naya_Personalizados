from django.http import JsonResponse
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(csrf_exempt, name='dispatch')
class AutoLogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'status': 'success', })
        return JsonResponse({'status': 'error', })


def heartbeat(request):
    """Mantém a sessão ativa"""
    if request.user.is_authenticated:
        # Atualizar a sessão
        request.session.modified = True
        return JsonResponse({'status': 'active'})
    return JsonResponse({'status': 'inactive'}, status=401)
