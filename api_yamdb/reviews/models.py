from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=256,
    )
    year = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(date.today().year)
        ]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
    )
    description = models.CharField(
        max_length=256,
        blank=True
    )

    genre = models.ManyToManyField(Genre)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_name_year'
            )
        ]
        ordering = ('pk',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    """Ресурс review: пользовательские обзоры произведений."""

    SCORE_CHOICES = list(zip(range(1, 11), range(1, 11)))

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review_titles',
        help_text='Оцениваемое произведение')
    text = models.TextField(
        'Текст обзора',
        help_text='Текст обзора')
    author = models.ForeignKey(
        User,
        verbose_name='Автор обзора',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Автор обзора'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка произведения',
        help_text='Оценка от 1 до 10',
        choices=SCORE_CHOICES,
        blank=True)
    pub_date = models.DateTimeField(
        'Дата и время написания обзора',
        auto_now_add=True
    )

    class Meta:

        ordering = ('-pub_date',)
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'

        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='only_one_review_on_autor'),
        ]


class Comments(models.Model):
    """Ресурс review: пользовательские обзоры произведений"""

    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comment',
        help_text='Комментарий к обзору')
    text = models.TextField(
        'Текст комментария',
        help_text='Текст комментария')
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Автор комментария'
    )
    pub_date = models.DateTimeField(
        'Дата и время написания комментария',
        auto_now_add=True
    )

    class Meta:

        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
