# Standard Library Imports
from __future__ import unicode_literals

# Third-Party Imports (Django)
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

###########################################################################
#  0. USER MANAGER FOR CUSTOMUSER MODEL
class MyUserManager(BaseUserManager):

    # 0.1 FUNCTION TO HANDLE NEW NORMAL USER CREATION
    def create_user(self,email,password=None,**extra_fields):
        print("IN creating user  ==========")
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def get_by_natural_key(self, username):
        """
        Normalize email before lookup so that varying case in the domain
        doesn’t block authentication.
        """
        email = self.normalize_email(username)
        return self.get(**{self.model.USERNAME_FIELD: email})

    # 0.2 FUNCTION TO HANDLE NEW ADMIN/SUPERUSER CREATION 
    def create_superuser(self,email,password=None,**extra_fields):

        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(email,password,**extra_fields)
    
    # 0.3 USING ONLY NON-DELETED USERS
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)