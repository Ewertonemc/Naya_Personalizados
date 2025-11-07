# organize_and_import_final.py
def main():
    # TUDO dentro de uma função para evitar reordenação
    import os
    import sys
    import django
    import shutil

    # Configure Django PRIMEIRO
    project_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_path)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

    # DEPOIS importe o resto
    from django.conf import settings
    from naya_site.models import CategoriaGaleria, ImagemGaleria

    def importar_imagens():
        print("Importando imagens...")

        pastas = {
            'destaques': 'Destaques',
            'sublimação': 'Sublimação',
            'transfer': 'Transfer',
            'kites': 'Kits',
        }

        for pasta, nome in pastas.items():
            caminho = f'media/galeria/{pasta}'
            if os.path.exists(caminho):
                cat, created = CategoriaGaleria.objects.get_or_create(
                    nome=nome, slug=pasta.lower()
                )

                for arquivo in os.listdir(caminho):
                    if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = f'galeria/{pasta}/{arquivo}'
                        if not ImagemGaleria.objects.filter(imagem=img_path).exists():
                            ImagemGaleria.objects.create(
                                categoria=cat,
                                imagem=img_path,
                                descricao=f"{nome} - {arquivo}"
                            )
                            print(f"✅ {pasta}/{arquivo}")

        print("🎉 Concluído!")
    importar_imagens()


if __name__ == "__main__":
    main()
