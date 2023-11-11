from uuid import uuid4
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from pre_configs.models import PreConfig
from utils import staticfiles


class Organization(models.Model):
    name = models.CharField(max_length=128)
    key = models.SlugField(max_length=128, unique=True, blank=True)
    description = models.TextField(
        max_length=512,
        null=True,
        blank=True,
    )
    members = models.ManyToManyField(
        get_user_model(),
        related_name="organizations",
        blank=True,
    )
    admin = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="admin_organizations",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.name)
            while Organization.objects.filter(key=self.key).exists():
                random_num = uuid4().hex[:6]
                self.key = f"{self.key}-{random_num}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(
        max_length=512,
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="products",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        PreConfig.objects.get_or_create(
            name="Default pre-config", data=staticfiles.DEFAULT_PRE_CONFIG, product=self
        )


class Repository(models.Model):
    class Meta:
        unique_together = (("key", "product"),)
        verbose_name_plural = "Repositories"

    name = models.CharField(max_length=128)
    key = models.SlugField(max_length=128, unique=False)
    description = models.TextField(
        max_length=512,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="repositories",
    )

    def save(self, *args, **kwargs):
        self.key = slugify(self.name)
        self.key = f"{self.product.key}-{self.key}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
