import re

from django.core.exceptions import ValidationError


def validate_user(value):
    """Проверка поля username модели user."""
    if value == 'me':
        raise ValidationError(
            f'Использовать имя {value} в качестве username запрещено.')
    elif re.findall(r'[^\w.@+-]+', value):
        raise ValidationError(
            'Required 150 characters or fewer, '
            'letters, digits and @/./+/-/_ only.')
