from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from datetime import datetime
from django.utils import timezone

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, password):
        user = self.model(email=email)
        user.password = password
        user.set_password(user.password)
        user.save()

    def create_staffuser(self, email, password):
        user = self.model(email=email)
        user.password = password
        user.set_password(user.password)
        # user.is_admin = True
        user.is_superuser = False
        user.is_staff = True
        user.is_active = True
        user.save()

    def create_superuser(self, email, password):
        user = self.model(email=email)
        # user.password=password
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

    def get_by_natural_key(self, email_):
        return self.get(email=email_)


class User(AbstractBaseUser, PermissionsMixin):
    admin_id = models.ForeignKey('self', related_name='User',on_delete=models.CASCADE, null=True)

    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(default=False, null=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    passport = models.CharField(max_length=300, blank=True, null=True)
    identityNumber = models.CharField(max_length=300, blank=True, null=True)

    dob = models.CharField(max_length=300, blank=True, null=True)
    phone =  models.CharField(max_length=300, blank=True, null=True)
    cell = models.CharField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    zip_code = models.CharField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=300, blank=True, null=True)
    
    trainingInstitute =models.CharField(max_length=300, blank=True, null=True)
    institutePhone = models.CharField(max_length=300, blank=True, null=True)
    facilitatorName = models.CharField(max_length=300, blank=True, null=True)
    institutionAccount = models.CharField(max_length=300, blank=True, null=True)
    instituteAddress = models.CharField(max_length=300, blank=True, null=True)
    instituteCity = models.CharField(max_length=300, blank=True, null=True)
    instituteZip = models.CharField(max_length=300, blank=True, null=True)
    instituteCountry = models.CharField(max_length=300, blank=True, null=True)
    registerName = models.CharField(max_length=300, blank=True, null=True)
    companyName = models.CharField(max_length=300, blank=True, null=True)
    accountStatus = models.BooleanField(default=False)
    GenderType = (
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        )

    gender = models.CharField(max_length=6, choices=GenderType, blank=True, default='Male', help_text='gender')
    email_verified_at = models.DateTimeField(default=timezone.now, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)

    # full_name = models.CharField(max_length=300, blank=True, null=True)

    # gender = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='user_image',  null=True)
    # o_auth_image = models.URLField(max_length = 200, null=True) 

    username = models.CharField(

        max_length=150,
        unique=True,
        null=True,

    )
    is_active = models.BooleanField(default=True)

    object = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_short_name(self):
        return self.email
