from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.Model):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    SUPERUSER = 'superuser'
    ANON = 'anonymous'
    CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (SUPERUSER, 'Суперюзер'),
        (ANON, 'Аноним'),
    ]


class User(AbstractUser):

    bio = models.TextField(
        max_length=500,
        blank=True
    )
    role = models.CharField(
        max_length=9,
        choices=UserRole.CHOICES,
        default=UserRole.USER,
        verbose_name='Уровень доступа'
    )

    @property
    def allowed_role(self):
        return self.role == UserRole.MODERATOR or self.role == UserRole.ADMIN

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    class Meta:
        ordering = ('username',)
