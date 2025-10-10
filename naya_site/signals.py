from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Orcamento, StatusOrcamento


@receiver(post_save, sender=Orcamento)
def notificar_mudanca_status(sender, instance, created, **kwargs):
    """Enviar notificações por email quando o status do orçamento mudar"""

    if created:
        # Novo orçamento criado - notificar empresa
        subject = f'Novo Orçamento Solicitado - #{instance.id}'
        message = f'''
        Um novo orçamento foi solicitado por {instance.cliente.get_full_name()}.
        
        ID: {instance.id}
        Cliente: {instance.cliente.get_full_name()}
        Data máxima: {instance.data_maxima_entrega}
        
        Acesse o painel administrativo para responder.
        '''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@nayapersonalizados.com'],  # Email da empresa
            fail_silently=True,
        )

    elif instance.status == StatusOrcamento.AGUARDANDO_CLIENTE:
        # Orçamento respondido - notificar cliente
        subject = f'Orçamento Respondido - #{instance.id}'
        message = f'''
        Olá {instance.cliente.get_full_name()},
        
        Seu orçamento foi analisado e está pronto para sua avaliação!
        
        Valor total: R$ {instance.get_valor_final()}
        Data prevista: {instance.data_prevista_entrega}
        
        Acesse sua conta para visualizar e responder.
        '''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.cliente.email],
            fail_silently=True,
        )
