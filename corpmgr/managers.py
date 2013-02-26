from django.db import models, IntegrityError
from django.contrib.contenttypes.models import ContentType, ContentTypeManager

class AppMgrMixin(models.Manager):
    def rejected(self):
        return self.get_query_set().filter(status=-1)

    def pending(self):
        return self.get_query_set().filter(status=1)

    def approved(self):
        return self.get_query_set().filter(status=2)

    def unknown(self):
        return self.get_query_set().exclude(status__in=(-1,1,2,3))

class CorporationAppMgr(AppMgrMixin):
    pass

class AllianceAppMgr(AppMgrMixin):
    pass

