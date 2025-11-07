# test_view.py
from naya_site import views
from django.test import RequestFactory
from naya_site.models import CategoriaGaleria, ImagemGaleria
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()


def testar_view():
    print("=== TESTANDO A VIEW ===")

    # Criar uma request falsa para testar
    factory = RequestFactory()
    request = factory.get('')

    # Chamar a view
    response = views.galeria_view(request)

    print(f"Status code: {response.status_code}")
    print(f"Template usado: {response.template_name}")

    # Verificar o contexto
    if hasattr(response, 'context_data'):
        print("Context data:", response.context_data)
    else:
        print("⚠️  Nenhum context_data encontrado")

    # Verificar dados diretamente
    categorias = CategoriaGaleria.objects.all()
    imagens = ImagemGaleria.objects.all()

    print(f"\n📊 Dados no banco:")
    print(f"Categorias: {categorias.count()}")
    print(f"Imagens: {imagens.count()}")

    for cat in categorias:
        print(f"  - {cat.nome}: {cat.imagemgaleria_set.count()} imagens")


if __name__ == "__main__":
    testar_view()
