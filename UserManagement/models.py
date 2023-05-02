from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager, AbstractUser

# Create your models here.
# class MyUserManager(BaseUserManager):
class MyUserManager(UserManager):

    def create_user(self, email, date_of_birth, username, password=None):
        if not email:
            raise ValueError('User must provide an email address')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, username, date_of_birth, password=None):
        user = self.create_user(
            email,
            username=username,
            date_of_birth=date_of_birth,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# class MyUser(AbstractBaseUser):
class MyUser(AbstractUser):
    # email = models.EmailField(verbose_name='email address', unique=True, max_length=255)
    # date_of_birth = models.DateField()
    # username = models.CharField(max_length=50)
    # is_admin = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)

    # USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = []

    # objects = MyUserManager()

    # def __str__(self):
    #     return str(self.email)
    
    # def has_perm(self):
    #     return self.is_superuser
    
    # def has_module_perms(self, app_label):
    #     return self.is_superuser

    # username = None
    username = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(verbose_name='email address', unique=True)

    # otp functionality starts
    otp = models.CharField(max_length=6)
    otp_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    # otp functionality stops

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'date_of_birth']

    objects = MyUserManager()