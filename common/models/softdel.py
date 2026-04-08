# Standard Library Imports
import uuid,logging,datetime

# Third-Party Imports (Django)
from django.db import models
from django.utils import timezone


logger = logging.getLogger('user')


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True,blank=True)

    def delete(self,using=None,keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
        logger.info(f"soft deleted the object {self.pk}")

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])  
        logger.info(f"Object {self} has been restored") 

    class Meta:
        abstract = True 
        