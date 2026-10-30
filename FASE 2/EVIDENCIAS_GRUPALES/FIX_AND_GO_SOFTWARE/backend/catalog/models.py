from django.db import models


class Category(models.Model):
    """Categoría de servicio técnico del hogar."""

    name = models.CharField('nombre', max_length=60, unique=True)
    slug = models.SlugField('slug', unique=True)
    description = models.TextField('descripción', blank=True)
    icon = models.CharField(
        'ícono', max_length=40, blank=True,
        help_text='Nombre de ícono para la app móvil.',
    )

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Commune(models.Model):
    """Comuna de Santiago donde se presta servicio."""

    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField('slug', unique=True)

    class Meta:
        verbose_name = 'comuna'
        verbose_name_plural = 'comunas'
        ordering = ['name']

    def __str__(self):
        return self.name
