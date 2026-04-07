# Standard Library Imports
from __future__ import unicode_literals

# Third-Party Imports (Django)
from django.contrib.auth.models import BaseUserManager

###########################################################################
#  0. USER MANAGER FOR CUSTOMUSER MODEL
class MyUserManager(BaseUserManager):

    # 0.1 FUNCTION TO HANDLE NEW NORMAL USER CREATION
    def create_user(self,email,password=None,**extra_fields):

        #logger.info("p6-create function inside usermanager ")
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        #logger.info("----p6.1-email checkd -----")
        user = self.model(email=email,**extra_fields)
        #logger.info("----p6.2-details stored -----")
        user.set_password(password)
        #logger.info("----p6.3-password stored-----")
        user.save(using=self.db)
        #logger.info("----p6.4-user saved-----")
        return user

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