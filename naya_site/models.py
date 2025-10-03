from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
import re


def upload_image(instance, filename):
    if instance.category:
        name = instance.category.name.lower().replace(' ', '_')
        return f'{name}/{filename}'
    else:
        return f'no_category/{filename}'


class State(models.Model):
    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'
        ordering = ['name']

    STATE_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),  ('PA', 'Pará'), ('PB', 'Paraíba'),
        ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    name = models.CharField(
        max_length=2, choices=STATE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(
        blank=True,
        upload_to=upload_image,
        null=True,
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    minimum_quantity = models.IntegerField(
        default=5,
        verbose_name='Minimum Quantity',
        help_text="Quantidade abaixo de minimo necessário em estoque",
    )
    unit_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    @property
    def total_value(self):
        return self.quantity * self.unit_value

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato: 000.000.000-00'
            )
        ]
    )

    # Endereço
    cep = models.CharField(max_length=9, validators=[
                           RegexValidator(regex=r'^\d{5}-\d{3}$')])
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        cpf_clean = re.sub(r'[^\d]', '', self.cpf)

        if not self.validar_cpf(cpf_clean):
            raise ValidationError({'cpf': 'CPF inválido'})

    def validar_cpf(self, cpf):

        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto

        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto

        return int(cpf[9]) == digito1 and int(cpf[10]) == digito2

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.cpf}"
