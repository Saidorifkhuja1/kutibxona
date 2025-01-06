from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.templatetags.static import static

PHONE_REGEX = RegexValidator(
    regex=r"^\+998([0-9][0-9]|99)\d{7}$",
    message="Please provide a valid phone number",
)

class UserManager(BaseUserManager):
    def create_user(self, phone_number, last_name, name, email, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number')
        if not name:
            raise ValueError('User must have a name')
        if not last_name:
            raise ValueError('User must have a last name')
        if not email:
            raise ValueError('User must have an email')

        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            name=name,
            last_name=last_name,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, last_name, name, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    family_name = models.CharField(max_length=250, default=False)
    id_card = models.CharField(max_length=50, default=False)
    education_level = models.CharField(max_length=100, default=False)
    work_place = models.CharField(max_length=250, blank=True)
    education_place = models.CharField(max_length=250, blank=True)
    home = models.CharField(max_length=250, default=False)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=21, unique=True, default="+998931112233")
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', default='accounts/avatars/avatar.jpg')
    deletion_date = models.DateTimeField(default=timezone.now())
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'name', 'last_name', 'family_name', 'id_card', 'education_level', 'home']

    def __str__(self):
        return f'{self.name} {self.last_name}'

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def formatted_deletion_date(self):
        return self.deletion_date.strftime('%Y-%m-%dT%H:%M')

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('accounts/avatars/avatar.jpg')

# /staticfiles