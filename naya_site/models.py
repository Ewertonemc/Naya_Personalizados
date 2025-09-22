from django.db import models
from django.core.validators import MinValueValidator


def upload_image(instance, filename):
    if instance.category:
        name = instance.category.name.lower().replace(' ', '_')
        return f'{name}/{filename}'
    else:
        return f'no_category/{filename}'


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
