from django.db import models


class Tags(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Тег',
        blank=False,
        null=False
    )
    slug = models.SlugField(
        verbose_name='slug',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name
