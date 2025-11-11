from django import template

register = template.Library()


@register.filter
def filter_by_tipo(arquivos, tipo_desejado):
    """
    Filtra arquivos por tipo
    Uso: {{ arquivos|filter_by_tipo:'empresa' }}
    """
    if hasattr(arquivos, 'filter'):
        return arquivos.filter(tipo=tipo_desejado)
    return [arquivo for arquivo in arquivos if getattr(arquivo, 'tipo', None) == tipo_desejado]


@register.filter
def filter_aprovados(arquivos):
    """
    Filtra arquivos aprovados
    Uso: {{ arquivos|filter_aprovados }}
    """
    if hasattr(arquivos, 'filter'):
        return arquivos.filter(aprovado_cliente=True)
    return [arquivo for arquivo in arquivos if getattr(arquivo, 'aprovado_cliente', False)]
