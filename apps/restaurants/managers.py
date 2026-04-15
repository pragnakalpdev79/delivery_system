# Standard Library Imports
from __future__ import unicode_literals

# Third-Party Imports (Django)
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

###########################################################################
#  0. USER MANAGER FOR CUSTOMUSER MODEL
class MyRestoManager(BaseUserManager):
    # 0.1 USING ONLY NON-DELETED USERS
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)