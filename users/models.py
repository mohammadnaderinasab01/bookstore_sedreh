from typing import Any
from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from utils.validators import only_int
import uuid


class UserManager(AbstractUserManager):
    """
    Custom user model manager where phonenumber is the unique identifiers
    for authentication instead of usernames.
    """    
    def create_user(self, phonenumber, password, **extra_fields):
        """
        Create and save a user with the given phonenumber and password.
        """
        if not phonenumber:
            raise ValueError(_("The Phonenumber must be set"))

        user = self.model(phonenumber=phonenumber, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, phonenumber, password, **extra_fields):
        """
        Create and save a SuperUser with the given phonenumber and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phonenumber, password, **extra_fields)
    
    

class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    phonenumber = models.CharField(max_length=10, unique=True, primary_key=False, validators=[only_int])
    password = models.CharField(max_length=255)
    username = None
    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = []

    objects = UserManager()
    

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        create_user_wallet(self)

def create_user_wallet(user):
    create_user_wallet = UserWallet.objects.create(user=user)
    create_user_wallet.save()
    return create_user_wallet

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    charge = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.phonenumber