from django.db import models

class APIKeyInfoManager(models.Manager):

    def corporations(self):
        return self.get_query_set().filter(key_type='CO')

    def characters(self):
        return self.get_query_set().filter(key_type='CH')

    def accounts(self):
        return self.get_query_set().filter(key_type='AC')
